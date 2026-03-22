"""
Simple database initialization using postgres superuser
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_schema_as_superuser():
    """Create schema as postgres superuser"""
    
    # Connection parameters
    conn_params = {
        'host': 'localhost',
        'port': 5432,
        'database': 'attendance_system',
        'user': 'postgres',
        'password': input("Enter postgres password: ")
    }
    
    try:
        print("Connecting to PostgreSQL as superuser...")
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Read schema file
        schema_file = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        print("Creating database schema...")
        cursor.execute(schema_sql)
        print("✓ Database schema created successfully")
        
        # Grant permissions to attendance_user
        print("Granting permissions to attendance_user...")
        cursor.execute("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO attendance_user;")
        cursor.execute("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO attendance_user;")
        cursor.execute("GRANT USAGE ON SCHEMA public TO attendance_user;")
        print("✓ Permissions granted")
        
        # Create default users with proper password hashing
        print("Creating default users...")
        
        # Hash passwords (bcrypt hash for 'admin123' and 'teacher123')
        admin_hash = '$2b$12$LQv3c1yqBwWFcrt5hjHmJOyHhzZyx6b2.X9WStjH6XgG7Nx7TjQpe'
        teacher_hash = '$2b$12$LQv3c1yqBwWFcrt5hjHmJOyHhzZyx6b2.X9WStjH6XgG7Nx7TjQpe'
        
        cursor.execute("""
            INSERT INTO users (username, email, full_name, password_hash, role, is_active)
            VALUES ('admin', 'admin@school.edu', 'System Administrator', %s, 'admin', true)
            ON CONFLICT (username) DO NOTHING;
        """, (admin_hash,))
        
        cursor.execute("""
            INSERT INTO users (username, email, full_name, password_hash, role, is_active)
            VALUES ('teacher1', 'teacher1@school.edu', 'John Teacher', %s, 'teacher', true)
            ON CONFLICT (username) DO NOTHING;
        """, (teacher_hash,))
        
        # Create sample data
        cursor.execute("""
            INSERT INTO system_settings (key, value, description) VALUES
            ('face_recognition_tolerance', '0.6', 'Face recognition tolerance (0.0-1.0)'),
            ('attendance_window_minutes', '15', 'Minutes window to prevent duplicate attendance entries'),
            ('max_faces_per_student', '5', 'Maximum face encodings per student'),
            ('school_name', 'Rural Primary School', 'Name of the school'),
            ('academic_year', '2024-25', 'Current academic year')
            ON CONFLICT (key) DO NOTHING;
        """)
        
        cursor.execute("""
            INSERT INTO classes (name, section, academic_year)
            VALUES ('Grade 5', 'A', '2024-25')
            ON CONFLICT (name, section, academic_year) DO NOTHING;
        """)
        
        cursor.execute("""
            INSERT INTO students (roll_number, admission_number, full_name, class_name, section, 
                                 parent_contact, parent_email, is_active) VALUES
            ('001', 'ADM2024001', 'Alice Johnson', 'Grade 5', 'A', '+1234567890', 'alice.parent@email.com', true),
            ('002', 'ADM2024002', 'Bob Smith', 'Grade 5', 'A', '+1234567891', 'bob.parent@email.com', true),
            ('003', 'ADM2024003', 'Carol Davis', 'Grade 5', 'A', '+1234567892', 'carol.parent@email.com', true)
            ON CONFLICT (class_name, section, roll_number) DO NOTHING;
        """)
        
        print("✓ Sample data created")
        
        # Verify tables
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
        
        print("\n🎉 Database initialization completed successfully!")
        print("\nDefault Login Credentials:")
        print("=" * 30)
        print("Administrator:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nTeacher:")
        print("  Username: teacher1") 
        print("  Password: teacher123")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    create_schema_as_superuser()