#!/usr/bin/env python3
"""
Simple script to create admin user for the attendance system
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///attendance_system.db')
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "instance", "attendance_system.db")

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Define User model (simplified)
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='teacher')
    full_name = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

def create_admin_user():
    """Create admin user"""
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✓ Database tables created/verified")
            
            # Check if admin already exists
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print("Admin user already exists")
                print(f"Username: {admin.username}")
                print(f"Email: {admin.email}")
                print(f"Role: {admin.role}")
                return True
            
            # Create new admin user
            admin = User(
                username='admin',
                email='admin@school.edu',
                full_name='System Administrator',
                role='admin'
            )
            admin.set_password('admin123')
            
            db.session.add(admin)
            db.session.commit()
            
            print("✓ Admin user created successfully!")
            print("Username: admin")
            print("Password: admin123")
            print("Email: admin@school.edu")
            print("Role: admin")
            
            return True
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        return False

if __name__ == '__main__':
    print("Creating admin user for Attendance System...")
    success = create_admin_user()
    if success:
        print("\n🎉 Admin user setup completed!")
        print("\nYou can now login with:")
        print("Username: admin")
        print("Password: admin123")
    else:
        print("\n❌ Failed to create admin user")
        sys.exit(1)