from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

class User(db.Model):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='teacher')  # teacher, admin, principal
    full_name = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Student(db.Model):
    """Student model for storing student information and face encodings"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    admission_number = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    date_of_birth = db.Column(db.Date)
    parent_contact = db.Column(db.String(15))
    parent_email = db.Column(db.String(120))
    address = db.Column(db.Text)
    face_encodings = db.Column(db.Text)  # JSON string of face encodings
    profile_image = db.Column(db.String(255))  # Path to profile image
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy=True)
    
    def set_face_encodings(self, encodings_list):
        """Store face encodings as JSON"""
        self.face_encodings = json.dumps(encodings_list)
    
    def get_face_encodings(self):
        """Retrieve face encodings from JSON"""
        if self.face_encodings:
            return json.loads(self.face_encodings)
        return []
    
    def to_dict(self):
        return {
            'id': self.id,
            'roll_number': self.roll_number,
            'admission_number': self.admission_number,
            'full_name': self.full_name,
            'class_name': self.class_name,
            'section': self.section,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'parent_contact': self.parent_contact,
            'parent_email': self.parent_email,
            'profile_image': self.profile_image,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AttendanceRecord(db.Model):
    """Attendance record model"""
    __tablename__ = 'attendance_records'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_in = db.Column(db.Time)
    time_out = db.Column(db.Time)
    status = db.Column(db.String(20), default='present')  # present, absent, late
    confidence_score = db.Column(db.Float)  # Face recognition confidence
    marked_by = db.Column(db.String(50), default='system')  # system, manual
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'date': self.date.isoformat() if self.date else None,
            'time_in': self.time_in.strftime('%H:%M:%S') if self.time_in else None,
            'time_out': self.time_out.strftime('%H:%M:%S') if self.time_out else None,
            'status': self.status,
            'confidence_score': self.confidence_score,
            'marked_by': self.marked_by,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Class(db.Model):
    """Class model for organizing students"""
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    academic_year = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    teacher = db.relationship('User', backref='classes')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'section': self.section,
            'teacher_name': self.teacher.full_name if self.teacher else None,
            'academic_year': self.academic_year,
            'is_active': self.is_active
        }

class AuditLog(db.Model):
    """Audit log for tracking system activities"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    table_name = db.Column(db.String(50))
    record_id = db.Column(db.Integer)
    old_values = db.Column(db.Text)  # JSON string
    new_values = db.Column(db.Text)  # JSON string
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='audit_logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user.full_name if self.user else 'System',
            'action': self.action,
            'table_name': self.table_name,
            'record_id': self.record_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SystemSettings(db.Model):
    """System settings and configuration"""
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }