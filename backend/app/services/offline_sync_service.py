from datetime import datetime, timedelta
import json
import os
import logging
import sqlite3
from app.models import AttendanceRecord, Student, User
from app import db

class OfflineSyncService:
    """Service for handling offline data synchronization"""
    
    def __init__(self):
        self.offline_db_path = 'offline_data.db'
        self.sync_interval = 300  # 5 minutes
        self.last_sync_time = None
        self.create_offline_tables()
    
    def create_offline_tables(self):
        """Create offline SQLite tables"""
        try:
            conn = sqlite3.connect(self.offline_db_path)
            cursor = conn.cursor()
            
            # Create offline attendance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS offline_attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    time_in TEXT,
                    status TEXT DEFAULT 'present',
                    confidence_score REAL,
                    marked_by TEXT DEFAULT 'system_offline',
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    synced INTEGER DEFAULT 0
                )
            ''')
            
            # Create offline students cache
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS offline_students (
                    id INTEGER PRIMARY KEY,
                    roll_number TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    class_name TEXT NOT NULL,
                    section TEXT NOT NULL,
                    face_encodings TEXT,
                    last_updated TEXT NOT NULL
                )
            ''')
            
            # Create sync log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sync_type TEXT NOT NULL,
                    records_count INTEGER DEFAULT 0,
                    success INTEGER DEFAULT 0,
                    error_message TEXT,
                    sync_time TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logging.info("Offline database tables created successfully")
        except Exception as e:
            logging.error(f"Error creating offline tables: {str(e)}")
    
    def store_offline_attendance(self, student_id, confidence_score, notes=None):
        """Store attendance record offline"""
        try:
            conn = sqlite3.connect(self.offline_db_path)
            cursor = conn.cursor()
            
            today = datetime.now().date().isoformat()
            current_time = datetime.now().time().isoformat()
            created_at = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO offline_attendance 
                (student_id, date, time_in, status, confidence_score, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (student_id, today, current_time, 'present', confidence_score, notes, created_at))
            
            conn.commit()
            conn.close()
            
            logging.info(f"Stored offline attendance for student {student_id}")
            return True, "Attendance stored offline successfully"
        
        except Exception as e:
            logging.error(f"Error storing offline attendance: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def cache_students_data(self):
        """Cache students data for offline use"""
        try:
            students = Student.query.filter_by(is_active=True).all()
            
            conn = sqlite3.connect(self.offline_db_path)
            cursor = conn.cursor()
            
            # Clear existing cache
            cursor.execute('DELETE FROM offline_students')
            
            # Insert current students data
            for student in students:
                cursor.execute('''
                    INSERT INTO offline_students 
                    (id, roll_number, full_name, class_name, section, face_encodings, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    student.id,
                    student.roll_number,
                    student.full_name,
                    student.class_name,
                    student.section,
                    student.face_encodings,
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            conn.close()
            
            logging.info(f"Cached {len(students)} students for offline use")
            return True, f"Cached {len(students)} students"
        
        except Exception as e:
            logging.error(f"Error caching students data: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def get_offline_students(self):
        """Get cached students data for offline recognition"""
        try:
            conn = sqlite3.connect(self.offline_db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM offline_students')
            rows = cursor.fetchall()
            
            students = []
            for row in rows:
                student = {
                    'id': row[0],
                    'roll_number': row[1],
                    'full_name': row[2],
                    'class_name': row[3],
                    'section': row[4],
                    'face_encodings': json.loads(row[5]) if row[5] else [],
                    'last_updated': row[6]
                }
                students.append(student)
            
            conn.close()
            return True, students
        
        except Exception as e:
            logging.error(f"Error getting offline students: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def sync_offline_data(self):
        """Sync offline data to main database"""
        try:
            conn = sqlite3.connect(self.offline_db_path)
            cursor = conn.cursor()
            
            # Get unsynced attendance records
            cursor.execute('SELECT * FROM offline_attendance WHERE synced = 0')
            offline_records = cursor.fetchall()
            
            synced_count = 0
            errors = []
            
            for record in offline_records:
                try:
                    # Create attendance record in main database
                    attendance = AttendanceRecord(
                        student_id=record[1],
                        date=datetime.fromisoformat(record[2]).date(),
                        time_in=datetime.fromisoformat(record[3]).time() if record[3] else None,
                        status=record[4],
                        confidence_score=record[5],
                        marked_by=record[6],
                        notes=record[7],
                        created_at=datetime.fromisoformat(record[8])
                    )
                    
                    db.session.add(attendance)
                    db.session.commit()
                    
                    # Mark as synced in offline database
                    cursor.execute('UPDATE offline_attendance SET synced = 1 WHERE id = ?', (record[0],))
                    synced_count += 1
                
                except Exception as e:
                    errors.append(f"Record {record[0]}: {str(e)}")
                    db.session.rollback()
            
            conn.commit()
            conn.close()
            
            # Log sync results
            self.log_sync_result('attendance', synced_count, len(errors) == 0, errors)
            self.last_sync_time = datetime.now()
            
            if errors:
                return False, f"Synced {synced_count} records with {len(errors)} errors"
            else:
                return True, f"Successfully synced {synced_count} attendance records"
        
        except Exception as e:
            logging.error(f"Error syncing offline data: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def log_sync_result(self, sync_type, records_count, success, errors):
        """Log synchronization results"""
        try:
            conn = sqlite3.connect(self.offline_db_path)
            cursor = conn.cursor()
            
            error_message = '; '.join(errors) if errors else None
            
            cursor.execute('''
                INSERT INTO sync_log (sync_type, records_count, success, error_message, sync_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (sync_type, records_count, 1 if success else 0, error_message, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            logging.error(f"Error logging sync result: {str(e)}")
    
    def get_sync_status(self):
        """Get synchronization status and statistics"""
        try:
            conn = sqlite3.connect(self.offline_db_path)
            cursor = conn.cursor()
            
            # Get pending records count
            cursor.execute('SELECT COUNT(*) FROM offline_attendance WHERE synced = 0')
            pending_count = cursor.fetchone()[0]
            
            # Get last sync info
            cursor.execute('SELECT * FROM sync_log ORDER BY sync_time DESC LIMIT 1')
            last_sync = cursor.fetchone()
            
            # Get total offline records
            cursor.execute('SELECT COUNT(*) FROM offline_attendance')
            total_offline_records = cursor.fetchone()[0]
            
            conn.close()
            
            status = {
                'pending_records': pending_count,
                'total_offline_records': total_offline_records,
                'last_sync_time': self.last_sync_time.isoformat() if self.last_sync_time else None,
                'last_sync_details': {
                    'sync_type': last_sync[1] if last_sync else None,
                    'records_count': last_sync[2] if last_sync else 0,
                    'success': bool(last_sync[3]) if last_sync else None,
                    'error_message': last_sync[4] if last_sync else None,
                    'sync_time': last_sync[5] if last_sync else None
                } if last_sync else None
            }
            
            return True, status
        
        except Exception as e:
            logging.error(f"Error getting sync status: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def is_online(self):
        """Check if system is online (simple connectivity test)"""
        try:
            # Try to query database
            db.session.execute('SELECT 1')
            return True
        except Exception:
            return False
    
    def auto_sync_if_online(self):
        """Automatically sync if online and sync interval has passed"""
        try:
            if not self.is_online():
                return False, "System is offline"
            
            # Check if sync interval has passed
            if self.last_sync_time:
                time_since_sync = datetime.now() - self.last_sync_time
                if time_since_sync.total_seconds() < self.sync_interval:
                    return False, "Sync interval not reached"
            
            # Perform sync
            return self.sync_offline_data()
        
        except Exception as e:
            logging.error(f"Error in auto sync: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def clear_synced_records(self, older_than_days=7):
        """Clear old synced records from offline database"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=older_than_days)).isoformat()
            
            conn = sqlite3.connect(self.offline_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM offline_attendance 
                WHERE synced = 1 AND created_at < ?
            ''', (cutoff_date,))
            
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logging.info(f"Cleared {deleted_count} old synced records")
            return True, f"Cleared {deleted_count} old records"
        
        except Exception as e:
            logging.error(f"Error clearing synced records: {str(e)}")
            return False, f"Error: {str(e)}"