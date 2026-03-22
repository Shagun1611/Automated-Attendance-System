from datetime import datetime, date, time
from app.models import AttendanceRecord, Student
from app import db
import logging

class AttendanceService:
    """Service for handling attendance operations"""
    
    def __init__(self):
        self.attendance_window_minutes = 15  # Window to prevent duplicate entries
    
    def mark_attendance(self, student_id, confidence_score, marked_by='system', notes=None):
        """Mark attendance for a student"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return False, "Student not found"
            
            today = date.today()
            current_time = datetime.now().time()
            
            # Check if attendance already marked today
            existing_record = AttendanceRecord.query.filter_by(
                student_id=student_id,
                date=today
            ).first()
            
            if existing_record:
                # Update time_out if it's later in the day
                if existing_record.time_in and current_time > existing_record.time_in:
                    existing_record.time_out = current_time
                    existing_record.updated_at = datetime.utcnow()
                    db.session.commit()
                    return True, f"Updated time out for {student.full_name}"
                else:
                    return False, f"Attendance already marked for {student.full_name} today"
            
            # Create new attendance record
            attendance_record = AttendanceRecord(
                student_id=student_id,
                date=today,
                time_in=current_time,
                status='present',
                confidence_score=confidence_score,
                marked_by=marked_by,
                notes=notes
            )
            
            db.session.add(attendance_record)
            db.session.commit()
            
            logging.info(f"Attendance marked for student {student.full_name} with confidence {confidence_score}")
            return True, f"Attendance marked for {student.full_name}"
        
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error marking attendance: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def mark_manual_attendance(self, student_id, attendance_date, status, user_id, notes=None):
        """Manually mark attendance (by teacher/admin)"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return False, "Student not found"
            
            # Check if record exists
            existing_record = AttendanceRecord.query.filter_by(
                student_id=student_id,
                date=attendance_date
            ).first()
            
            if existing_record:
                # Update existing record
                existing_record.status = status
                existing_record.notes = notes
                existing_record.marked_by = f'user_{user_id}'
                existing_record.updated_at = datetime.utcnow()
            else:
                # Create new record
                attendance_record = AttendanceRecord(
                    student_id=student_id,
                    date=attendance_date,
                    status=status,
                    marked_by=f'user_{user_id}',
                    notes=notes
                )
                db.session.add(attendance_record)
            
            db.session.commit()
            return True, f"Manual attendance updated for {student.full_name}"
        
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error marking manual attendance: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def get_attendance_by_date(self, attendance_date, class_name=None, section=None):
        """Get attendance records for a specific date"""
        try:
            query = db.session.query(AttendanceRecord, Student).join(Student)
            query = query.filter(AttendanceRecord.date == attendance_date)
            
            if class_name:
                query = query.filter(Student.class_name == class_name)
            
            if section:
                query = query.filter(Student.section == section)
            
            records = query.all()
            
            attendance_list = []
            for record, student in records:
                attendance_data = record.to_dict()
                attendance_data['student_info'] = student.to_dict()
                attendance_list.append(attendance_data)
            
            return True, attendance_list
        
        except Exception as e:
            logging.error(f"Error getting attendance by date: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def get_student_attendance_history(self, student_id, start_date=None, end_date=None):
        """Get attendance history for a specific student"""
        try:
            query = AttendanceRecord.query.filter_by(student_id=student_id)
            
            if start_date:
                query = query.filter(AttendanceRecord.date >= start_date)
            
            if end_date:
                query = query.filter(AttendanceRecord.date <= end_date)
            
            records = query.order_by(AttendanceRecord.date.desc()).all()
            
            attendance_history = []
            for record in records:
                attendance_history.append(record.to_dict())
            
            return True, attendance_history
        
        except Exception as e:
            logging.error(f"Error getting student attendance history: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def get_attendance_statistics(self, class_name=None, section=None, start_date=None, end_date=None):
        """Get attendance statistics"""
        try:
            # Base query for students
            student_query = Student.query.filter_by(is_active=True)
            
            if class_name:
                student_query = student_query.filter(Student.class_name == class_name)
            
            if section:
                student_query = student_query.filter(Student.section == section)
            
            students = student_query.all()
            
            # Base query for attendance records
            attendance_query = db.session.query(AttendanceRecord).join(Student)
            
            if class_name:
                attendance_query = attendance_query.filter(Student.class_name == class_name)
            
            if section:
                attendance_query = attendance_query.filter(Student.section == section)
            
            if start_date:
                attendance_query = attendance_query.filter(AttendanceRecord.date >= start_date)
            
            if end_date:
                attendance_query = attendance_query.filter(AttendanceRecord.date <= end_date)
            
            # Calculate statistics
            total_students = len(students)
            total_records = attendance_query.count()
            present_records = attendance_query.filter(AttendanceRecord.status == 'present').count()
            absent_records = attendance_query.filter(AttendanceRecord.status == 'absent').count()
            
            attendance_percentage = (present_records / total_records * 100) if total_records > 0 else 0
            
            # Get daily attendance summary
            daily_summary = db.session.query(
                AttendanceRecord.date,
                db.func.count(AttendanceRecord.id).label('total'),
                db.func.sum(db.case([(AttendanceRecord.status == 'present', 1)], else_=0)).label('present')
            ).join(Student)
            
            if class_name:
                daily_summary = daily_summary.filter(Student.class_name == class_name)
            
            if section:
                daily_summary = daily_summary.filter(Student.section == section)
            
            if start_date:
                daily_summary = daily_summary.filter(AttendanceRecord.date >= start_date)
            
            if end_date:
                daily_summary = daily_summary.filter(AttendanceRecord.date <= end_date)
            
            daily_data = daily_summary.group_by(AttendanceRecord.date).all()
            
            daily_stats = []
            for day_data in daily_data:
                daily_stats.append({
                    'date': day_data.date.isoformat(),
                    'total': day_data.total,
                    'present': day_data.present,
                    'percentage': (day_data.present / day_data.total * 100) if day_data.total > 0 else 0
                })
            
            statistics = {
                'total_students': total_students,
                'total_records': total_records,
                'present_records': present_records,
                'absent_records': absent_records,
                'attendance_percentage': round(attendance_percentage, 2),
                'daily_statistics': daily_stats
            }
            
            return True, statistics
        
        except Exception as e:
            logging.error(f"Error getting attendance statistics: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def get_irregular_attendance_alerts(self, days_threshold=3):
        """Get students with irregular attendance patterns"""
        try:
            from datetime import timedelta
            
            end_date = date.today()
            start_date = end_date - timedelta(days=days_threshold)
            
            # Get students with consecutive absences
            students_query = db.session.query(Student).filter_by(is_active=True)
            
            irregular_students = []
            
            for student in students_query:
                # Count recent absences
                recent_records = AttendanceRecord.query.filter_by(
                    student_id=student.id
                ).filter(
                    AttendanceRecord.date >= start_date,
                    AttendanceRecord.date <= end_date
                ).order_by(AttendanceRecord.date.desc()).all()
                
                absent_days = len([r for r in recent_records if r.status == 'absent'])
                total_days = len(recent_records)
                
                if absent_days >= days_threshold or (total_days > 0 and absent_days / total_days > 0.5):
                    irregular_students.append({
                        'student': student.to_dict(),
                        'absent_days': absent_days,
                        'total_days': total_days,
                        'absence_rate': (absent_days / total_days * 100) if total_days > 0 else 0
                    })
            
            return True, irregular_students
        
        except Exception as e:
            logging.error(f"Error getting irregular attendance alerts: {str(e)}")
            return False, f"Error: {str(e)}"