import pandas as pd
import requests
import json
import os
from datetime import datetime, date
from app.models import AttendanceRecord, Student
from app import db
import logging

class PowerBIService:
    """Service for Power BI integration and data export"""
    
    def __init__(self):
        self.workspace_id = os.getenv('POWERBI_WORKSPACE_ID')
        self.dataset_id = os.getenv('POWERBI_DATASET_ID')
        self.client_id = os.getenv('POWERBI_CLIENT_ID')
        self.client_secret = os.getenv('POWERBI_CLIENT_SECRET')
        self.access_token = None
    
    def authenticate(self):
        """Authenticate with Power BI API"""
        try:
            url = "https://login.microsoftonline.com/common/oauth2/token"
            
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'resource': 'https://analysis.windows.net/powerbi/api'
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                return True, "Authentication successful"
            else:
                return False, f"Authentication failed: {response.text}"
        
        except Exception as e:
            logging.error(f"Power BI authentication error: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def export_attendance_data(self, start_date=None, end_date=None):
        """Export attendance data for Power BI"""
        try:
            # Query attendance data
            query = db.session.query(AttendanceRecord, Student).join(Student)
            
            if start_date:
                query = query.filter(AttendanceRecord.date >= start_date)
            
            if end_date:
                query = query.filter(AttendanceRecord.date <= end_date)
            
            records = query.all()
            
            # Prepare data for export
            export_data = []
            for attendance, student in records:
                record = {
                    'date': attendance.date.isoformat(),
                    'student_id': student.id,
                    'student_name': student.full_name,
                    'roll_number': student.roll_number,
                    'class': student.class_name,
                    'section': student.section,
                    'status': attendance.status,
                    'time_in': attendance.time_in.strftime('%H:%M:%S') if attendance.time_in else None,
                    'time_out': attendance.time_out.strftime('%H:%M:%S') if attendance.time_out else None,
                    'confidence_score': attendance.confidence_score,
                    'marked_by': attendance.marked_by,
                    'created_at': attendance.created_at.isoformat() if attendance.created_at else None
                }
                export_data.append(record)
            
            return True, export_data
        
        except Exception as e:
            logging.error(f"Error exporting attendance data: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def export_to_excel(self, data, filename=None):
        """Export data to Excel file"""
        try:
            if not filename:
                filename = f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            df = pd.DataFrame(data)
            
            # Create exports directory if it doesn't exist
            exports_dir = 'exports'
            os.makedirs(exports_dir, exist_ok=True)
            
            filepath = os.path.join(exports_dir, filename)
            df.to_excel(filepath, index=False)
            
            return True, filepath
        
        except Exception as e:
            logging.error(f"Error exporting to Excel: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def export_to_csv(self, data, filename=None):
        """Export data to CSV file"""
        try:
            if not filename:
                filename = f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            df = pd.DataFrame(data)
            
            # Create exports directory if it doesn't exist
            exports_dir = 'exports'
            os.makedirs(exports_dir, exist_ok=True)
            
            filepath = os.path.join(exports_dir, filename)
            df.to_csv(filepath, index=False)
            
            return True, filepath
        
        except Exception as e:
            logging.error(f"Error exporting to CSV: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def push_to_powerbi(self, data):
        """Push data to Power BI dataset"""
        try:
            if not self.access_token:
                auth_success, auth_message = self.authenticate()
                if not auth_success:
                    return False, auth_message
            
            url = f"https://api.powerbi.com/v1.0/myorg/groups/{self.workspace_id}/datasets/{self.dataset_id}/rows"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Format data for Power BI
            powerbi_data = {
                "rows": data
            }
            
            response = requests.post(url, headers=headers, json=powerbi_data)
            
            if response.status_code == 200:
                return True, "Data successfully pushed to Power BI"
            else:
                return False, f"Failed to push data: {response.text}"
        
        except Exception as e:
            logging.error(f"Error pushing to Power BI: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def get_dashboard_url(self):
        """Get Power BI dashboard URL"""
        try:
            if not self.workspace_id:
                return False, "Power BI workspace not configured"
            
            dashboard_url = f"https://app.powerbi.com/groups/{self.workspace_id}/dashboards"
            return True, dashboard_url
        
        except Exception as e:
            logging.error(f"Error getting dashboard URL: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def generate_attendance_summary(self, start_date=None, end_date=None):
        """Generate attendance summary for Power BI"""
        try:
            # Get attendance statistics
            query = db.session.query(AttendanceRecord).join(Student)
            
            if start_date:
                query = query.filter(AttendanceRecord.date >= start_date)
            
            if end_date:
                query = query.filter(AttendanceRecord.date <= end_date)
            
            # Daily summary
            daily_summary = db.session.query(
                AttendanceRecord.date,
                db.func.count(AttendanceRecord.id).label('total_records'),
                db.func.sum(db.case([(AttendanceRecord.status == 'present', 1)], else_=0)).label('present_count'),
                db.func.sum(db.case([(AttendanceRecord.status == 'absent', 1)], else_=0)).label('absent_count'),
                db.func.sum(db.case([(AttendanceRecord.status == 'late', 1)], else_=0)).label('late_count')
            ).join(Student).group_by(AttendanceRecord.date).all()
            
            summary_data = []
            for record in daily_summary:
                attendance_rate = (record.present_count / record.total_records * 100) if record.total_records > 0 else 0
                
                summary_data.append({
                    'date': record.date.isoformat(),
                    'total_records': record.total_records,
                    'present_count': record.present_count,
                    'absent_count': record.absent_count,
                    'late_count': record.late_count,
                    'attendance_rate': round(attendance_rate, 2)
                })
            
            return True, summary_data
        
        except Exception as e:
            logging.error(f"Error generating attendance summary: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def sync_all_data(self):
        """Sync all attendance data to Power BI"""
        try:
            # Export attendance data
            success, data = self.export_attendance_data()
            if not success:
                return False, data
            
            # Push to Power BI
            success, message = self.push_to_powerbi(data)
            if not success:
                return False, message
            
            # Generate and push summary data
            success, summary_data = self.generate_attendance_summary()
            if success:
                # You might want to push summary to a different dataset
                pass
            
            return True, "All data synchronized successfully"
        
        except Exception as e:
            logging.error(f"Error syncing all data: {str(e)}")
            return False, f"Error: {str(e)}"