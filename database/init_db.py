"""
Database initialization and setup script for Automated Attendance System
"""

from app import app, db
from app.models import User, Student, AttendanceRecord, Class, AuditLog, SystemSettings
from datetime import datetime, date
import logging

def create_tables():
    """Create all database tables"""
    try:
        with app.app_context():
            db.create_all()
            print("Database tables created successfully")
            return True
    except Exception as e:
        logging.error(f"Error creating tables: {str(e)}")
        return False

def create_default_admin():
    """Create default admin user"""
    try:
        with app.app_context():
            # Check if admin already exists
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@school.edu',
                    full_name='System Administrator',
                    role='admin'
                )
                admin.set_password('admin123')  # Change this in production
                
                db.session.add(admin)
                db.session.commit()
                print("Default admin user created (username: admin, password: admin123)")
            else:
                print("Admin user already exists")
        return True
    except Exception as e:
        logging.error(f"Error creating admin user: {str(e)}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    try:
        with app.app_context():
            # Create sample teacher
            teacher = User.query.filter_by(username='teacher1').first()
            if not teacher:
                teacher = User(
                    username='teacher1',
                    email='teacher1@school.edu',
                    full_name='John Teacher',
                    role='teacher'
                )
                teacher.set_password('teacher123')
                db.session.add(teacher)
            
            # Create sample class
            sample_class = Class.query.filter_by(name='Grade 5', section='A').first()
            if not sample_class:
                sample_class = Class(
                    name='Grade 5',
                    section='A',
                    teacher_id=teacher.id,
                    academic_year='2024-25'
                )
                db.session.add(sample_class)
            
            # Create sample students
            sample_students = [
                {
                    'roll_number': 'G5A001',
                    'admission_number': 'ADM2024001',
                    'full_name': 'Alice Johnson',
                    'class_name': 'Grade 5',
                    'section': 'A',
                    'parent_contact': '+1234567890',
                    'parent_email': 'alice.parent@email.com'
                },
                {
                    'roll_number': 'G5A002',
                    'admission_number': 'ADM2024002',
                    'full_name': 'Bob Smith',
                    'class_name': 'Grade 5',
                    'section': 'A',
                    'parent_contact': '+1234567891',
                    'parent_email': 'bob.parent@email.com'
                },
                {
                    'roll_number': 'G5A003',
                    'admission_number': 'ADM2024003',
                    'full_name': 'Carol Davis',
                    'class_name': 'Grade 5',
                    'section': 'A',
                    'parent_contact': '+1234567892',
                    'parent_email': 'carol.parent@email.com'
                }
            ]
            
            for student_data in sample_students:
                existing_student = Student.query.filter_by(
                    roll_number=student_data['roll_number']
                ).first()
                
                if not existing_student:
                    student = Student(**student_data)
                    db.session.add(student)
            
            # Create default system settings
            default_settings = [
                {
                    'key': 'face_recognition_tolerance',
                    'value': '0.6',
                    'description': 'Face recognition tolerance (0.0-1.0)'
                },
                {
                    'key': 'attendance_window_minutes',
                    'value': '15',
                    'description': 'Minutes window to prevent duplicate attendance entries'
                },
                {
                    'key': 'max_faces_per_student',
                    'value': '5',
                    'description': 'Maximum face encodings per student'
                },
                {
                    'key': 'school_name',
                    'value': 'Rural Primary School',
                    'description': 'Name of the school'
                },
                {
                    'key': 'academic_year',
                    'value': '2024-25',
                    'description': 'Current academic year'
                }
            ]
            
            for setting_data in default_settings:
                existing_setting = SystemSettings.query.filter_by(
                    key=setting_data['key']
                ).first()
                
                if not existing_setting:
                    setting = SystemSettings(**setting_data)
                    db.session.add(setting)
            
            db.session.commit()
            print("Sample data created successfully")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating sample data: {str(e)}")
        return False

def initialize_database():
    """Initialize the complete database"""
    print("Initializing Automated Attendance System Database...")
    
    success = True
    
    # Create tables
    if create_tables():
        print("✓ Database tables created")
    else:
        print("✗ Failed to create database tables")
        success = False
    
    # Create default admin
    if create_default_admin():
        print("✓ Default admin user created")
    else:
        print("✗ Failed to create default admin user")
        success = False
    
    # Create sample data
    if create_sample_data():
        print("✓ Sample data created")
    else:
        print("✗ Failed to create sample data")
        success = False
    
    if success:
        print("\n🎉 Database initialization completed successfully!")
        print("\nDefault Login Credentials:")
        print("Username: admin")
        print("Password: admin123")
        print("Role: Administrator")
        print("\nTeacher Login:")
        print("Username: teacher1")
        print("Password: teacher123")
        print("Role: Teacher")
    else:
        print("\n❌ Database initialization completed with errors")
    
    return success

if __name__ == '__main__':
    initialize_database()