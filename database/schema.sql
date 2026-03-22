-- SQL Schema for Automated Attendance System
-- PostgreSQL Database Schema

-- Create database (run this separately)
-- CREATE DATABASE attendance_db;
-- \c attendance_db;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table for authentication and authorization
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'teacher' CHECK (role IN ('teacher', 'admin', 'principal')),
    full_name VARCHAR(200) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Classes table
CREATE TABLE classes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    section VARCHAR(10) NOT NULL,
    teacher_id INTEGER REFERENCES users(id),
    academic_year VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, section, academic_year)
);

-- Students table
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    roll_number VARCHAR(50) NOT NULL,
    admission_number VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    class_name VARCHAR(50) NOT NULL,
    section VARCHAR(10) NOT NULL,
    date_of_birth DATE,
    parent_contact VARCHAR(15),
    parent_email VARCHAR(120),
    address TEXT,
    face_encodings TEXT, -- JSON string of face encodings
    profile_image VARCHAR(255), -- Path to profile image
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_students_class_section_roll UNIQUE (class_name, section, roll_number)
);

-- Attendance records table
CREATE TABLE attendance_records (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    time_in TIME,
    time_out TIME,
    status VARCHAR(20) DEFAULT 'present' CHECK (status IN ('present', 'absent', 'late', 'excused')),
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    marked_by VARCHAR(50) DEFAULT 'system',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, date)
);

-- Audit logs table
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(50),
    record_id INTEGER,
    old_values TEXT, -- JSON string
    new_values TEXT, -- JSON string
    ip_address INET,
    user_agent VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System settings table
CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_students_class_section ON students(class_name, section);
-- Optional: keep index on roll_number for searches, but uniqueness is composite above
CREATE INDEX idx_students_roll_number ON students(roll_number);
CREATE INDEX idx_attendance_student_date ON attendance_records(student_id, date);
CREATE INDEX idx_attendance_date ON attendance_records(date);
CREATE INDEX idx_attendance_status ON attendance_records(status);
CREATE INDEX idx_audit_logs_user_action ON audit_logs(user_id, action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- Functions and Triggers

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updating timestamps
CREATE TRIGGER update_users_modtime 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_students_modtime 
    BEFORE UPDATE ON students 
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_attendance_modtime 
    BEFORE UPDATE ON attendance_records 
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_settings_modtime 
    BEFORE UPDATE ON system_settings 
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- Views for common queries

-- Daily attendance summary view
CREATE VIEW daily_attendance_summary AS
SELECT 
    ar.date,
    s.class_name,
    s.section,
    COUNT(*) as total_students,
    COUNT(CASE WHEN ar.status = 'present' THEN 1 END) as present_count,
    COUNT(CASE WHEN ar.status = 'absent' THEN 1 END) as absent_count,
    COUNT(CASE WHEN ar.status = 'late' THEN 1 END) as late_count,
    ROUND(
        (COUNT(CASE WHEN ar.status = 'present' THEN 1 END) * 100.0 / COUNT(*)), 2
    ) as attendance_percentage
FROM attendance_records ar
JOIN students s ON ar.student_id = s.id
WHERE s.is_active = true
GROUP BY ar.date, s.class_name, s.section
ORDER BY ar.date DESC, s.class_name, s.section;

-- Student attendance summary view
CREATE VIEW student_attendance_summary AS
SELECT 
    s.id,
    s.roll_number,
    s.full_name,
    s.class_name,
    s.section,
    COUNT(ar.id) as total_records,
    COUNT(CASE WHEN ar.status = 'present' THEN 1 END) as present_days,
    COUNT(CASE WHEN ar.status = 'absent' THEN 1 END) as absent_days,
    COUNT(CASE WHEN ar.status = 'late' THEN 1 END) as late_days,
    ROUND(
        (COUNT(CASE WHEN ar.status = 'present' THEN 1 END) * 100.0 / 
         NULLIF(COUNT(ar.id), 0)), 2
    ) as attendance_percentage
FROM students s
LEFT JOIN attendance_records ar ON s.id = ar.student_id
WHERE s.is_active = true
GROUP BY s.id, s.roll_number, s.full_name, s.class_name, s.section
ORDER BY s.class_name, s.section, s.roll_number;

-- Insert default system settings
INSERT INTO system_settings (key, value, description) VALUES
('face_recognition_tolerance', '0.6', 'Face recognition tolerance (0.0-1.0)'),
('attendance_window_minutes', '15', 'Minutes window to prevent duplicate attendance entries'),
('max_faces_per_student', '5', 'Maximum face encodings per student'),
('school_name', 'Rural Primary School', 'Name of the school'),
('academic_year', '2024-25', 'Current academic year'),
('school_start_time', '08:00', 'School start time'),
('school_end_time', '15:00', 'School end time'),
('timezone', 'UTC', 'System timezone'),
('auto_sync_enabled', 'true', 'Enable automatic data synchronization'),
('sync_interval_seconds', '300', 'Synchronization interval in seconds');

-- Insert default admin user (password: admin123)
-- Note: This should be done through the application for proper password hashing
-- INSERT INTO users (username, email, full_name, role, password_hash) VALUES
-- ('admin', 'admin@school.edu', 'System Administrator', 'admin', 'hashed_password_here');

COMMENT ON TABLE users IS 'User accounts for system access';
COMMENT ON TABLE students IS 'Student information and face recognition data';
COMMENT ON TABLE attendance_records IS 'Daily attendance tracking records';
COMMENT ON TABLE classes IS 'Class and section organization';
COMMENT ON TABLE audit_logs IS 'System activity audit trail';
COMMENT ON TABLE system_settings IS 'Configurable system parameters';

COMMENT ON COLUMN students.face_encodings IS 'JSON array of face recognition encodings';
COMMENT ON COLUMN attendance_records.confidence_score IS 'Face recognition confidence (0.0-1.0)';
COMMENT ON COLUMN attendance_records.marked_by IS 'Who marked the attendance (system/user_id)';