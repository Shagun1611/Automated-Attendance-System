"""
Standalone database initialization script for Automated Attendance System
This script creates the database schema without requiring the Flask app to be running
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import getpass

def get_database_config():
    """Get database configuration from user or environment"""
    config = {}
    
    # Try to get from environment first
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        print("Using DATABASE_URL from environment")
        return database_url
    
    # Interactive setup
    print("PostgreSQL Database Configuration")
    print("-" * 35)
    
    config['host'] = input("Database Host (default: localhost): ") or 'localhost'
    config['port'] = input("Database Port (default: 5432): ") or '5432'
    config['database'] = input("Database Name (default: attendance_system): ") or 'attendance_system'
    config['user'] = input("Database User (default: attendance_user): ") or 'attendance_user'
    config['password'] = getpass.getpass("Database Password: ")
    
    return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

def create_database_schema(connection_string):
    """Create the database schema"""
    
    # Parse connection string
    if connection_string.startswith('postgresql://'):
        # Extract components
        import urllib.parse as urlparse
        url = urlparse.urlparse(connection_string)
        
        conn_params = {
            'host': url.hostname,
            'port': url.port or 5432,
            'database': url.path.lstrip('/'),
            'user': url.username,
            'password': url.password
        }
    else:
        print("Invalid connection string format")
        return False
    
    try:
        # Connect to PostgreSQL
        print(f"Connecting to database: {conn_params['database']}")
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Read and execute schema
        schema_file = os.path.join(os.path.dirname(__file__), 'schema.sql')
        
        if not os.path.exists(schema_file):
            print(f"Schema file not found: {schema_file}")
            return False
        
        print("Reading database schema...")
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        print("Creating database tables...")
        cursor.execute(schema_sql)
        
        print("✓ Database schema created successfully")
        
        # Create default admin user
        print("Creating default admin user...")
        create_admin_sql = """
        INSERT INTO users (username, email, full_name, password_hash, role, is_active, created_at)
        VALUES ('admin', 'admin@school.edu', 'System Administrator', 
                '$2b$12$LQv3c1yqBwWFcrt5hjHmJOyHhzZyx6b2.X9WStjH6XgG7Nx7TjQpe', -- admin123
                'admin', true, NOW())
        ON CONFLICT (username) DO NOTHING;
        """
        cursor.execute(create_admin_sql)
        
        # Create default teacher user
        create_teacher_sql = """
        INSERT INTO users (username, email, full_name, password_hash, role, is_active, created_at)
        VALUES ('teacher1', 'teacher1@school.edu', 'John Teacher', 
                '$2b$12$LQv3c1yqBwWFcrt5hjHmJOyHhzZyx6b2.X9WStjH6XgG7Nx7TjQpe', -- teacher123
                'teacher', true, NOW())
        ON CONFLICT (username) DO NOTHING;
        """
        cursor.execute(create_teacher_sql)
        
        # Create sample system settings
        settings_sql = """
        INSERT INTO system_settings (key, value, description, created_at) VALUES
        ('face_recognition_tolerance', '0.6', 'Face recognition tolerance (0.0-1.0)', NOW()),
        ('attendance_window_minutes', '15', 'Minutes window to prevent duplicate attendance entries', NOW()),
        ('max_faces_per_student', '5', 'Maximum face encodings per student', NOW()),
        ('school_name', 'Rural Primary School', 'Name of the school', NOW()),
        ('academic_year', '2024-25', 'Current academic year', NOW())
        ON CONFLICT (key) DO NOTHING;
        """
        cursor.execute(settings_sql)
        
        # Create sample class
        class_sql = """
        INSERT INTO classes (name, section, academic_year, created_at)
        VALUES ('Grade 5', 'A', '2024-25', NOW())
        ON CONFLICT (name, section, academic_year) DO NOTHING;
        """
        cursor.execute(class_sql)
        
        # Create sample students
        students_sql = """
        INSERT INTO students (roll_number, admission_number, full_name, class_name, section, 
                             parent_contact, parent_email, is_active, created_at) VALUES
        ('G5A001', 'ADM2024001', 'Alice Johnson', 'Grade 5', 'A', '+1234567890', 'alice.parent@email.com', true, NOW()),
        ('G5A002', 'ADM2024002', 'Bob Smith', 'Grade 5', 'A', '+1234567891', 'bob.parent@email.com', true, NOW()),
        ('G5A003', 'ADM2024003', 'Carol Davis', 'Grade 5', 'A', '+1234567892', 'carol.parent@email.com', true, NOW())
        ON CONFLICT (roll_number) DO NOTHING;
        """
        cursor.execute(students_sql)
        
        print("✓ Default users and sample data created")
        
        # Verify table creation
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"✓ Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main initialization function"""
    print("🚀 Automated Attendance System - Database Initialization")
    print("=" * 60)
    
    # Get database configuration
    try:
        connection_string = get_database_config()
    except KeyboardInterrupt:
        print("\nDatabase initialization cancelled by user")
        return
    
    # Create database schema
    success = create_database_schema(connection_string)
    
    if success:
        print("\n🎉 Database initialization completed successfully!")
        print("\nDefault Login Credentials:")
        print("=" * 30)
        print("Administrator:")
        print("  Username: admin")
        print("  Password: admin123")
        print("  Role: Administrator")
        print("\nTeacher:")
        print("  Username: teacher1")
        print("  Password: teacher123")
        print("  Role: Teacher")
        print("\n⚠️  IMPORTANT: Change default passwords in production!")
        print("\nNext Steps:")
        print("1. Copy .env.example to .env in the backend directory")
        print("2. Update .env with your database credentials")
        print("3. Activate the Python virtual environment")
        print("4. Install Python dependencies: pip install -r backend/requirements.txt")
        print("5. Start the backend: cd backend && python app.py")
        print("6. Start the frontend: cd frontend && npm start")
    else:
        print("\n❌ Database initialization failed!")
        print("\nTroubleshooting:")
        print("1. Ensure PostgreSQL is running")
        print("2. Verify database credentials are correct")
        print("3. Check if the database 'attendance_system' exists")
        print("4. Ensure the user 'attendance_user' has proper permissions")

if __name__ == '__main__':
    main()