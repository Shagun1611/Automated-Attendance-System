from datetime import datetime
from flask import request, g
from functools import wraps
import hashlib
import os
import logging
from cryptography.fernet import Fernet
from app.models import AuditLog, User
from app import db
import json

class SecurityService:
    """Service for handling security-related operations"""
    
    def __init__(self):
        self.encryption_key = self.get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def get_or_create_encryption_key(self):
        """Get or create encryption key for data protection"""
        key_file = 'encryption.key'
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            logging.info("New encryption key generated")
        
        return key
    
    def encrypt_data(self, data):
        """Encrypt sensitive data"""
        try:
            if isinstance(data, str):
                data = data.encode()
            
            encrypted_data = self.cipher_suite.encrypt(data)
            return encrypted_data.decode()
        
        except Exception as e:
            logging.error(f"Error encrypting data: {str(e)}")
            return None
    
    def decrypt_data(self, encrypted_data):
        """Decrypt sensitive data"""
        try:
            if isinstance(encrypted_data, str):
                encrypted_data = encrypted_data.encode()
            
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            return decrypted_data.decode()
        
        except Exception as e:
            logging.error(f"Error decrypting data: {str(e)}")
            return None
    
    def hash_password(self, password):
        """Hash password with salt"""
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt + key
    
    def verify_password(self, stored_password, provided_password):
        """Verify password against stored hash"""
        salt = stored_password[:32]
        stored_key = stored_password[32:]
        new_key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
        return stored_key == new_key
    
    def validate_password_strength(self, password):
        """Validate password strength according to policy"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        return len(errors) == 0, errors
    
    def generate_secure_token(self, length=32):
        """Generate secure random token"""
        return os.urandom(length).hex()

class AuditService:
    """Service for handling audit logging"""
    
    @staticmethod
    def log_action(user_id, action, table_name=None, record_id=None, old_values=None, new_values=None):
        """Log user action for audit purposes"""
        try:
            # Get request information
            ip_address = None
            user_agent = None
            
            if request:
                ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
                user_agent = request.headers.get('User-Agent', '')
            
            # Create audit log entry
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                table_name=table_name,
                record_id=record_id,
                old_values=json.dumps(old_values) if old_values else None,
                new_values=json.dumps(new_values) if new_values else None,
                ip_address=ip_address,
                user_agent=user_agent[:255] if user_agent else None  # Limit length
            )
            
            db.session.add(audit_log)
            db.session.commit()
            
            logging.info(f"Audit log created: User {user_id} performed {action}")
        
        except Exception as e:
            logging.error(f"Error creating audit log: {str(e)}")
            db.session.rollback()

def audit_log(action, table_name=None):
    """Decorator for automatic audit logging"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = getattr(g, 'current_user_id', None)
            
            try:
                result = func(*args, **kwargs)
                
                # Log successful action
                AuditService.log_action(
                    user_id=user_id,
                    action=f"{action}_SUCCESS",
                    table_name=table_name
                )
                
                return result
            
            except Exception as e:
                # Log failed action
                AuditService.log_action(
                    user_id=user_id,
                    action=f"{action}_FAILED",
                    table_name=table_name
                )
                raise e
        
        return wrapper
    return decorator

def require_role(required_roles):
    """Decorator to require specific user roles"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user = getattr(g, 'current_user', None)
            
            if not current_user:
                return {'error': 'Authentication required'}, 401
            
            if isinstance(required_roles, str):
                required_roles_list = [required_roles]
            else:
                required_roles_list = required_roles
            
            if current_user.role not in required_roles_list:
                AuditService.log_action(
                    user_id=current_user.id,
                    action='UNAUTHORIZED_ACCESS_ATTEMPT',
                    table_name='users'
                )
                return {'error': 'Insufficient permissions'}, 403
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

class SessionManager:
    """Manage user sessions and security"""
    
    def __init__(self):
        self.failed_attempts = {}  # Track failed login attempts
        self.max_attempts = 5
        self.lockout_duration = 1800  # 30 minutes in seconds
    
    def record_failed_attempt(self, username, ip_address):
        """Record failed login attempt"""
        key = f"{username}:{ip_address}"
        current_time = datetime.utcnow()
        
        if key not in self.failed_attempts:
            self.failed_attempts[key] = []
        
        self.failed_attempts[key].append(current_time)
        
        # Clean old attempts
        self.failed_attempts[key] = [
            attempt for attempt in self.failed_attempts[key]
            if (current_time - attempt).total_seconds() < self.lockout_duration
        ]
        
        # Log security event
        AuditService.log_action(
            user_id=None,
            action='FAILED_LOGIN_ATTEMPT',
            old_values={'username': username, 'ip_address': ip_address}
        )
    
    def is_locked_out(self, username, ip_address):
        """Check if user/IP is locked out"""
        key = f"{username}:{ip_address}"
        
        if key not in self.failed_attempts:
            return False
        
        current_time = datetime.utcnow()
        
        # Clean old attempts
        self.failed_attempts[key] = [
            attempt for attempt in self.failed_attempts[key]
            if (current_time - attempt).total_seconds() < self.lockout_duration
        ]
        
        return len(self.failed_attempts[key]) >= self.max_attempts
    
    def clear_failed_attempts(self, username, ip_address):
        """Clear failed attempts after successful login"""
        key = f"{username}:{ip_address}"
        
        if key in self.failed_attempts:
            del self.failed_attempts[key]

class DataValidator:
    """Validate and sanitize input data"""
    
    @staticmethod
    def validate_student_data(data):
        """Validate student registration data"""
        errors = []
        
        required_fields = ['roll_number', 'admission_number', 'full_name', 'class_name', 'section']
        
        for field in required_fields:
            if not data.get(field) or not str(data.get(field)).strip():
                errors.append(f"{field.replace('_', ' ').title()} is required")
        
        # Validate roll number format
        roll_number = data.get('roll_number', '').strip()
        if roll_number and not roll_number.isalnum():
            errors.append("Roll number must contain only letters and numbers")
        
        # Validate email if provided
        parent_email = data.get('parent_email', '').strip()
        if parent_email:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, parent_email):
                errors.append("Invalid parent email format")
        
        # Validate phone number if provided
        parent_contact = data.get('parent_contact', '').strip()
        if parent_contact:
            # Remove common separators
            clean_contact = re.sub(r'[^\d+]', '', parent_contact)
            if len(clean_contact) < 10:
                errors.append("Parent contact must be at least 10 digits")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_input(data):
        """Sanitize input data to prevent injection attacks"""
        if isinstance(data, dict):
            return {key: DataValidator.sanitize_input(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [DataValidator.sanitize_input(item) for item in data]
        elif isinstance(data, str):
            # Basic HTML/SQL injection prevention
            import html
            return html.escape(data.strip())
        else:
            return data

# Initialize services
security_service = SecurityService()
session_manager = SessionManager()