# System Administrator Manual

## Table of Contents
1. [Administrator Overview](#administrator-overview)
2. [System Configuration](#system-configuration)
3. [User Management](#user-management)
4. [Data Management](#data-management)
5. [System Monitoring](#system-monitoring)
6. [Security Management](#security-management)
7. [Backup and Recovery](#backup-and-recovery)
8. [Troubleshooting Guide](#troubleshooting-guide)

---

## Administrator Overview

### Administrator Responsibilities

As a system administrator, you are responsible for:
- **System Configuration**: Managing system settings and parameters
- **User Management**: Creating, modifying, and deactivating user accounts
- **Data Integrity**: Ensuring data accuracy and consistency
- **Security**: Maintaining system security and access controls
- **Performance**: Monitoring and optimizing system performance
- **Backup**: Ensuring regular data backups and recovery procedures

### Administrator Dashboard

Upon logging in as an administrator, you have access to:
- **System Overview**: Current status, statistics, and alerts
- **User Management Panel**: Complete user administration tools
- **System Settings**: Configuration options for all system components
- **Audit Logs**: Complete system activity monitoring
- **Reports**: Advanced reporting and analytics tools
- **Maintenance Tools**: System health and performance monitoring

---

## System Configuration

### General Settings

#### Access System Settings
1. Login with administrator credentials
2. Navigate to **Settings** → **System Configuration**
3. Modify settings as needed
4. Save changes and restart services if required

#### Key Configuration Options

**Application Settings**
```json
{
  "app_name": "Automated Attendance System",
  "timezone": "UTC",
  "date_format": "YYYY-MM-DD",
  "time_format": "HH:MM:SS",
  "session_timeout": 1800,
  "max_login_attempts": 5,
  "lockout_duration": 900
}
```

**Face Recognition Settings**
```json
{
  "recognition_tolerance": 0.6,
  "confidence_threshold": 0.4,
  "model_type": "hog",
  "processing_interval": 2,
  "max_faces_per_frame": 10,
  "face_detection_timeout": 30
}
```

**Attendance Settings**
```json
{
  "auto_mark_attendance": true,
  "late_arrival_threshold": 15,
  "early_departure_threshold": 30,
  "grace_period_minutes": 5,
  "allow_manual_correction": true,
  "require_approval_for_changes": false
}
```

### Database Configuration

#### Connection Settings
- **Host**: Database server address
- **Port**: Database connection port (default: 5432)
- **Database Name**: attendance_system
- **Connection Pool**: Maximum concurrent connections
- **Timeout Settings**: Connection and query timeouts

#### Performance Tuning
```sql
-- Optimize PostgreSQL for attendance system
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Reload configuration
SELECT pg_reload_conf();
```

### Email Configuration

Configure SMTP settings for system notifications:
```json
{
  "smtp_server": "smtp.your-domain.com",
  "smtp_port": 587,
  "use_tls": true,
  "username": "system@your-domain.com",
  "password": "secure_password",
  "from_address": "attendance-system@your-domain.com",
  "admin_email": "admin@your-domain.com"
}
```

---

## User Management

### Creating User Accounts

#### Add New User
1. Navigate to **Users** → **Add New User**
2. Fill in user information:
   - **Username**: Unique identifier
   - **Full Name**: User's complete name
   - **Email**: Valid email address
   - **Role**: Select appropriate role
   - **Department**: User's department/class
   - **Status**: Active/Inactive

3. Set permissions based on role:
   - **Administrator**: Full system access
   - **Teacher**: Class management and attendance
   - **Principal**: Oversight and reporting access

#### User Role Configuration

**Administrator Permissions:**
- User management (create, edit, delete)
- System configuration access
- Complete data access
- Audit log access
- Backup and maintenance tools
- Advanced reporting features

**Teacher Permissions:**
- View assigned students
- Mark and modify attendance for assigned classes
- Generate class reports
- Register new students (if enabled)
- Access basic analytics

**Principal Permissions:**
- View all attendance data
- Generate comprehensive reports
- Access system analytics
- Monitor user activity
- Limited user management (view only)

### Managing Existing Users

#### Edit User Information
1. Find user in the user list
2. Click **Edit** next to user name
3. Modify required fields
4. Update permissions if needed
5. Save changes

#### Deactivate/Reactivate Users
```sql
-- Deactivate user account
UPDATE users SET is_active = false WHERE username = 'username';

-- Reactivate user account
UPDATE users SET is_active = true WHERE username = 'username';

-- Reset user password
UPDATE users SET password_hash = '$2b$12$newhashedpassword', 
                 must_change_password = true 
WHERE username = 'username';
```

#### Password Management
- **Reset Password**: Generate temporary password, force change on next login
- **Password Policy**: Enforce minimum length, complexity requirements
- **Password Expiry**: Set automatic password expiration (optional)

### Bulk User Operations

#### Import Users from CSV
```csv
username,full_name,email,role,department,status
teacher1,John Smith,john.smith@school.edu,teacher,Mathematics,active
teacher2,Jane Doe,jane.doe@school.edu,teacher,English,active
principal1,Robert Johnson,robert.johnson@school.edu,principal,Administration,active
```

#### Export User Data
```bash
# Export all users to CSV
psql -U attendance_user -d attendance_system -c "
COPY (SELECT username, full_name, email, role, department, created_at, last_login 
      FROM users WHERE is_active = true) 
TO 'users_export.csv' WITH CSV HEADER;"
```

---

## Data Management

### Student Data Administration

#### Bulk Student Import
1. Prepare CSV file with student data:
```csv
roll_number,admission_number,full_name,class,section,date_of_birth,parent_contact
001,ADM001,Alice Johnson,10,A,2008-05-15,+1234567890
002,ADM002,Bob Smith,10,A,2008-03-22,+1234567891
```

2. Navigate to **Students** → **Import Students**
3. Upload CSV file
4. Review and confirm import
5. Handle any validation errors

#### Student Data Validation
```sql
-- Check for duplicate entries
SELECT roll_number, COUNT(*) 
FROM students 
GROUP BY roll_number 
HAVING COUNT(*) > 1;

-- Validate required fields
SELECT * FROM students 
WHERE full_name IS NULL 
   OR roll_number IS NULL 
   OR class IS NULL;

-- Check face encoding data
SELECT student_id, full_name 
FROM students 
WHERE face_encodings IS NULL 
   OR face_encodings = '[]';
```

### Attendance Data Management

#### Attendance Data Cleanup
```sql
-- Remove duplicate attendance records
DELETE FROM attendance_records a1 
USING attendance_records a2 
WHERE a1.id < a2.id 
  AND a1.student_id = a2.student_id 
  AND a1.date = a2.date 
  AND a1.time_in = a2.time_in;

-- Fix invalid attendance times
UPDATE attendance_records 
SET time_in = '09:00:00' 
WHERE time_in < '06:00:00' 
   OR time_in > '12:00:00';
```

#### Data Export Options
```sql
-- Export attendance for specific period
COPY (
  SELECT s.roll_number, s.full_name, ar.date, ar.time_in, ar.time_out, ar.status
  FROM attendance_records ar
  JOIN students s ON ar.student_id = s.id
  WHERE ar.date BETWEEN '2024-01-01' AND '2024-01-31'
  ORDER BY ar.date, s.roll_number
) TO 'attendance_january_2024.csv' WITH CSV HEADER;
```

### Data Integrity Checks

#### Regular Maintenance Queries
```sql
-- Check orphaned attendance records
SELECT ar.id, ar.student_id, ar.date 
FROM attendance_records ar 
LEFT JOIN students s ON ar.student_id = s.id 
WHERE s.id IS NULL;

-- Validate user permissions
SELECT u.username, u.role, COUNT(p.id) as permission_count
FROM users u 
LEFT JOIN user_permissions p ON u.id = p.user_id 
GROUP BY u.id, u.username, u.role;

-- Check system log integrity
SELECT date_trunc('day', created_at) as day, 
       COUNT(*) as log_entries,
       COUNT(DISTINCT user_id) as active_users
FROM audit_logs 
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY date_trunc('day', created_at)
ORDER BY day DESC;
```

---

## System Monitoring

### Performance Monitoring

#### Key Performance Indicators
- **Response Time**: API endpoint response times
- **Database Performance**: Query execution times
- **Face Recognition Speed**: Processing time per face
- **System Resources**: CPU, memory, disk usage
- **Concurrent Users**: Active user sessions

#### Monitoring Tools Setup

**Application Performance Monitoring**
```python
# Add to Flask app
import time
from functools import wraps

def monitor_performance(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # Log performance metrics
        logger.info(f"Function {f.__name__} took {execution_time:.2f} seconds")
        
        return result
    return decorated_function
```

**Database Performance Monitoring**
```sql
-- Monitor slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements 
WHERE mean_time > 1000
ORDER BY mean_time DESC
LIMIT 10;

-- Check database connections
SELECT count(*), state 
FROM pg_stat_activity 
GROUP BY state;

-- Monitor table sizes
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### System Health Checks

#### Automated Health Monitoring
```bash
#!/bin/bash
# health_check.sh

# Check web service
curl -f http://localhost:5000/api/health || echo "Web service down"

# Check database connectivity
psql -U attendance_user -d attendance_system -c "SELECT 1" || echo "Database connection failed"

# Check Redis connectivity
redis-cli ping || echo "Redis connection failed"

# Check disk space
DISK_USAGE=$(df / | grep -vE '^Filesystem|tmpfs|cdrom' | awk '{ print $5 }' | sed 's/%//g')
if [ $DISK_USAGE -gt 80 ]; then
    echo "Warning: Disk usage is ${DISK_USAGE}%"
fi

# Check memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')
if (( $(echo "$MEMORY_USAGE > 85" | bc -l) )); then
    echo "Warning: Memory usage is ${MEMORY_USAGE}%"
fi
```

### Alert Configuration

#### Email Alerts Setup
```python
# alerts.py
import smtplib
from email.mime.text import MIMEText

def send_alert(subject, message, priority='medium'):
    if priority == 'high':
        recipients = ['admin@school.edu', 'tech@school.edu']
    else:
        recipients = ['admin@school.edu']
    
    for recipient in recipients:
        msg = MIMEText(message)
        msg['Subject'] = f"[ATTENDANCE SYSTEM] {subject}"
        msg['From'] = 'system@school.edu'
        msg['To'] = recipient
        
        # Send email
        server = smtplib.SMTP('localhost')
        server.send_message(msg)
        server.quit()

# Usage examples
send_alert("High CPU Usage", "CPU usage exceeded 90% for 5 minutes", "high")
send_alert("Database Backup Completed", "Daily backup completed successfully", "low")
```

---

## Security Management

### Access Control

#### Role-Based Permissions
```sql
-- Create custom roles
INSERT INTO roles (name, description) VALUES
('data_analyst', 'Read-only access to attendance data'),
('class_coordinator', 'Manage specific classes only'),
('parent_viewer', 'View own child attendance only');

-- Assign specific permissions
INSERT INTO role_permissions (role_id, permission) VALUES
((SELECT id FROM roles WHERE name = 'data_analyst'), 'view_reports'),
((SELECT id FROM roles WHERE name = 'data_analyst'), 'export_data'),
((SELECT id FROM roles WHERE name = 'class_coordinator'), 'manage_students'),
((SELECT id FROM roles WHERE name = 'class_coordinator'), 'mark_attendance');
```

#### IP Access Control
```python
# app.py - Add IP filtering
from flask import request, abort

ALLOWED_IPS = ['192.168.1.0/24', '10.0.0.0/16']

@app.before_request
def limit_remote_addr():
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    
    # Check if IP is in allowed ranges
    if not any(ip_address(client_ip) in ip_network(allowed_ip) 
              for allowed_ip in ALLOWED_IPS):
        abort(403)  # Forbidden
```

### Audit Logging

#### Enable Comprehensive Logging
```python
# Enhanced audit logging
def log_user_action(user_id, action, resource, details=None):
    audit_entry = {
        'user_id': user_id,
        'action': action,
        'resource': resource,
        'details': details,
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'timestamp': datetime.utcnow()
    }
    
    # Save to database
    db.session.add(AuditLog(**audit_entry))
    db.session.commit()

# Usage in routes
@app.route('/api/students/<int:student_id>', methods=['DELETE'])
@jwt_required()
def delete_student(student_id):
    current_user = get_jwt_identity()
    
    # Delete student
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    
    # Log the action
    log_user_action(
        current_user['id'], 
        'DELETE', 
        f'student:{student_id}',
        f'Deleted student: {student.full_name}'
    )
```

#### Security Audit Queries
```sql
-- Failed login attempts
SELECT u.username, COUNT(*) as failed_attempts, 
       MAX(al.created_at) as last_attempt
FROM audit_logs al 
JOIN users u ON al.user_id = u.id 
WHERE al.action = 'LOGIN_FAILED' 
  AND al.created_at > NOW() - INTERVAL '24 hours'
GROUP BY u.username 
HAVING COUNT(*) > 5
ORDER BY failed_attempts DESC;

-- Privilege escalation attempts
SELECT u.username, al.action, al.resource, al.created_at
FROM audit_logs al 
JOIN users u ON al.user_id = u.id 
WHERE al.action IN ('UNAUTHORIZED_ACCESS', 'PERMISSION_DENIED')
  AND al.created_at > NOW() - INTERVAL '7 days'
ORDER BY al.created_at DESC;

-- Data export activities
SELECT u.username, al.details, al.created_at
FROM audit_logs al 
JOIN users u ON al.user_id = u.id 
WHERE al.action = 'EXPORT_DATA'
  AND al.created_at > NOW() - INTERVAL '30 days'
ORDER BY al.created_at DESC;
```

### Data Encryption

#### Encrypt Sensitive Data
```python
# encryption.py - Enhanced encryption utilities
from cryptography.fernet import Fernet
import base64
import os

class DataEncryption:
    def __init__(self):
        self.key = os.environ.get('ENCRYPTION_KEY', '').encode()
        self.cipher = Fernet(self.key)
    
    def encrypt_face_encoding(self, encoding_data):
        """Encrypt face encoding data"""
        if not encoding_data:
            return None
        
        # Convert to bytes and encrypt
        data_bytes = str(encoding_data).encode()
        encrypted_data = self.cipher.encrypt(data_bytes)
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_face_encoding(self, encrypted_data):
        """Decrypt face encoding data"""
        if not encrypted_data:
            return None
        
        try:
            # Decode and decrypt
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(encrypted_bytes)
            return eval(decrypted_data.decode())  # Convert back to list
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None
```

---

## Backup and Recovery

### Automated Backup Strategy

#### Full System Backup Script
```bash
#!/bin/bash
# full_backup.sh

BACKUP_DIR="/var/backups/attendance"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
echo "Starting database backup..."
pg_dump -U attendance_user -h localhost attendance_system | gzip > $BACKUP_DIR/database_$DATE.sql.gz

# File system backup
echo "Starting file system backup..."
tar -czf $BACKUP_DIR/files_$DATE.tar.gz \
    /path/to/attendance/system/uploads \
    /path/to/attendance/system/logs \
    /path/to/attendance/system/config

# Configuration backup
echo "Backing up configuration files..."
cp /path/to/attendance/system/.env $BACKUP_DIR/env_$DATE.backup
cp /path/to/attendance/system/config/settings.json $BACKUP_DIR/settings_$DATE.json

# Verify backup integrity
echo "Verifying backup integrity..."
gunzip -t $BACKUP_DIR/database_$DATE.sql.gz
if [ $? -eq 0 ]; then
    echo "Database backup verified successfully"
else
    echo "Database backup verification failed"
    exit 1
fi

# Cleanup old backups
find $BACKUP_DIR -type f -mtime +$RETENTION_DAYS -delete

# Log backup completion
echo "Backup completed successfully at $(date)" >> $BACKUP_DIR/backup.log

# Send notification
echo "Backup completed successfully" | mail -s "Attendance System Backup - $DATE" admin@school.edu
```

### Recovery Procedures

#### Database Recovery
```bash
#!/bin/bash
# restore_database.sh

BACKUP_FILE=$1
if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    exit 1
fi

# Stop application
sudo systemctl stop attendance-backend

# Create database backup before restore
pg_dump -U attendance_user attendance_system > pre_restore_backup.sql

# Drop and recreate database
dropdb -U postgres attendance_system
createdb -U postgres attendance_system
psql -U postgres -d attendance_system -c "CREATE USER attendance_user WITH PASSWORD 'password';"
psql -U postgres -d attendance_system -c "GRANT ALL PRIVILEGES ON DATABASE attendance_system TO attendance_user;"

# Restore from backup
gunzip -c $BACKUP_FILE | psql -U attendance_user attendance_system

# Verify restoration
RECORD_COUNT=$(psql -U attendance_user -d attendance_system -t -c "SELECT COUNT(*) FROM users;")
if [ $RECORD_COUNT -gt 0 ]; then
    echo "Database restore completed successfully. Records found: $RECORD_COUNT"
else
    echo "Database restore may have failed. No records found."
    exit 1
fi

# Restart application
sudo systemctl start attendance-backend
```

#### Point-in-Time Recovery
```sql
-- Enable point-in-time recovery
ALTER SYSTEM SET wal_level = 'replica';
ALTER SYSTEM SET archive_mode = 'on';
ALTER SYSTEM SET archive_command = 'cp %p /var/backups/attendance/wal/%f';

-- Restart PostgreSQL to apply changes
-- sudo systemctl restart postgresql

-- Create base backup
-- pg_basebackup -U attendance_user -D /var/backups/attendance/base -Ft -z -P
```

### Disaster Recovery Plan

#### Recovery Time Objectives (RTO)
- **Critical Systems**: 2 hours
- **Full System Restore**: 4 hours
- **Data Recovery**: 1 hour

#### Recovery Point Objectives (RPO)
- **Database**: 15 minutes (with WAL archiving)
- **Files**: 24 hours (daily backups)
- **Configuration**: 24 hours (daily backups)

#### Emergency Procedures
1. **Assess the situation**: Determine scope of failure
2. **Notify stakeholders**: Alert users about downtime
3. **Implement backup procedures**: Switch to manual attendance if needed
4. **Begin recovery process**: Follow documented procedures
5. **Test system functionality**: Verify all components work correctly
6. **Resume normal operations**: Gradually restore full functionality
7. **Post-incident review**: Document lessons learned

---

## Troubleshooting Guide

### Common Administrative Issues

#### 1. User Cannot Login

**Symptoms**: User receives authentication error

**Diagnostic Steps**:
```sql
-- Check user account status
SELECT username, is_active, locked_until, failed_login_attempts 
FROM users WHERE username = 'problem_user';

-- Check recent login attempts
SELECT * FROM audit_logs 
WHERE user_id = (SELECT id FROM users WHERE username = 'problem_user')
  AND action IN ('LOGIN_SUCCESS', 'LOGIN_FAILED')
ORDER BY created_at DESC LIMIT 10;
```

**Solutions**:
- Reset password if forgotten
- Unlock account if locked due to failed attempts
- Activate account if deactivated
- Check role permissions

#### 2. Face Recognition Accuracy Issues

**Symptoms**: Students not being recognized consistently

**Diagnostic Steps**:
```python
# Check face encoding quality
def analyze_face_encodings():
    students = Student.query.all()
    for student in students:
        if student.face_encodings:
            encoding_count = len(json.loads(student.face_encodings))
            print(f"{student.full_name}: {encoding_count} encodings")
        else:
            print(f"{student.full_name}: No face encodings")
```

**Solutions**:
- Re-register face encodings with better lighting
- Adjust recognition tolerance in settings
- Clean camera lens
- Update face encodings periodically

#### 3. Database Performance Issues

**Symptoms**: Slow query response times

**Diagnostic Steps**:
```sql
-- Check database locks
SELECT blocked_locks.pid AS blocked_pid,
       blocked_activity.usename AS blocked_user,
       blocking_locks.pid AS blocking_pid,
       blocking_activity.usename AS blocking_user,
       blocked_activity.query AS blocked_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM attendance_records 
WHERE date >= '2024-01-01' AND date <= '2024-12-31';
```

**Solutions**:
- Add database indexes for frequently queried columns
- Optimize queries with proper WHERE clauses
- Regular VACUUM and ANALYZE operations
- Consider partitioning large tables

### Emergency Procedures

#### System Outage Response
1. **Immediate Actions**:
   - Check system status dashboard
   - Verify network connectivity
   - Check server resource usage
   - Review recent system logs

2. **Communication**:
   - Notify all users of the outage
   - Provide estimated resolution time
   - Activate manual backup procedures

3. **Recovery Steps**:
   - Implement backup attendance methods
   - Begin systematic troubleshooting
   - Document all actions taken
   - Test system thoroughly before resuming

#### Data Corruption Response
1. **Stop all write operations** immediately
2. **Assess the extent of corruption**
3. **Restore from most recent clean backup**
4. **Implement point-in-time recovery if needed**
5. **Verify data integrity after restoration**
6. **Resume operations with monitoring**

---

## Maintenance Schedule

### Daily Tasks
- [ ] Monitor system performance metrics
- [ ] Review error logs for issues
- [ ] Check backup completion status
- [ ] Verify face recognition accuracy
- [ ] Monitor user activity for anomalies

### Weekly Tasks
- [ ] Review and archive old log files
- [ ] Check database performance metrics
- [ ] Update system documentation
- [ ] Review user access permissions
- [ ] Test backup restoration procedures

### Monthly Tasks
- [ ] Perform comprehensive security audit
- [ ] Review and update user accounts
- [ ] Analyze attendance data for trends
- [ ] Update face encodings if needed
- [ ] Review system capacity planning

### Quarterly Tasks
- [ ] Full system security assessment
- [ ] Disaster recovery plan testing
- [ ] Performance optimization review
- [ ] User training and documentation update
- [ ] Hardware and software upgrade planning

---

*This administrator manual is version 1.0 - Last updated: October 2025*
*For technical assistance: admin-support@attendance-system.com*