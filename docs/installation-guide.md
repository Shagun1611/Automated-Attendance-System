# Technical Installation and Deployment Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [Database Setup](#database-setup)
4. [Configuration](#configuration)
5. [Deployment Options](#deployment-options)
6. [Security Configuration](#security-configuration)
7. [Maintenance and Updates](#maintenance-and-updates)
8. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Server Specifications

**Minimum Requirements:**
- **CPU**: 4 cores, 2.5 GHz
- **RAM**: 8 GB
- **Storage**: 100 GB SSD
- **Network**: 10 Mbps internet connection
- **OS**: Ubuntu 20.04 LTS / Windows Server 2019 / CentOS 8

**Recommended Specifications:**
- **CPU**: 8 cores, 3.0 GHz
- **RAM**: 16 GB
- **Storage**: 500 GB SSD
- **Network**: 50 Mbps internet connection
- **GPU**: Optional - NVIDIA GPU for faster face processing

### Software Dependencies

**Backend Requirements:**
```
Python 3.9+
PostgreSQL 12+
Redis 6+ (for caching)
Nginx (for production)
```

**Client Requirements:**
```
Modern web browser with WebRTC support
HD webcam (720p minimum, 1080p recommended)
Microphone (optional)
```

---

## Installation Steps

### 1. Environment Setup

#### Ubuntu/Linux Installation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.9 python3.9-pip python3.9-venv -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Redis
sudo apt install redis-server -y

# Install system dependencies for OpenCV
sudo apt install libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 libgstreamer1.0-0 -y

# Install CMake and build essentials
sudo apt install cmake build-essential -y
```

#### Windows Installation

1. **Install Python 3.9+**
   - Download from python.org
   - Ensure "Add to PATH" is checked during installation

2. **Install PostgreSQL**
   - Download PostgreSQL 14+ from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)
   - During installation:
     - Remember the superuser (postgres) password
     - Keep default port 5432
     - Select "Add to PATH" or note installation directory
   - Default installation path: `C:\Program Files\PostgreSQL\[version]\bin`

3. **Add PostgreSQL to PATH (if not done automatically)**
   ```powershell
   # Add to your PowerShell profile or system PATH
   $env:PATH += ";C:\Program Files\PostgreSQL\14\bin"
   ```

4. **Install Git**
   - Download from git-scm.com

5. **Install Visual Studio Build Tools**
   - Required for compiling Python packages with C extensions

6. **Install Node.js**
   - Download from nodejs.org (LTS version recommended)

### 2. Project Setup

```bash
# Clone the repository
git clone <your-repository-url>
cd automated-attendance-system

# Create virtual environment
python -m venv attendance_env

# Activate virtual environment
# On Linux/Mac:
source attendance_env/bin/activate
# On Windows:
attendance_env\Scripts\activate

# Install Python dependencies
pip install -r backend/requirements.txt

# Install Node.js dependencies for frontend
cd frontend
# If you encounter dependency conflicts, use --legacy-peer-deps
npm install
# Alternative: npm install --legacy-peer-deps
cd ..
```

---

## Database Setup

### 1. PostgreSQL Configuration

#### Create Database and User

**For Linux/Ubuntu:**
```sql
-- Connect to PostgreSQL as superuser
sudo -u postgres psql

-- Create database and user
CREATE DATABASE attendance_system;
CREATE USER attendance_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE attendance_system TO attendance_user;

-- Connect to the database
\c attendance_system

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Exit PostgreSQL
\q
```

**For Windows:**
```powershell
# First, add PostgreSQL to PATH (adjust version number as needed)
$env:PATH += ";C:\Program Files\PostgreSQL\18\bin"

# Connect to PostgreSQL using psql (use the password you set during installation)
psql -U postgres -h localhost
```

```sql
-- Create database and user (run each command one at a time)
CREATE DATABASE attendance_system;
CREATE USER attendance_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE attendance_system TO attendance_user;

-- Connect to the database
\c attendance_system

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Exit PostgreSQL
\q
```

**Common Windows PostgreSQL Issues:**
- **If you get syntax errors**: Make sure each SQL command ends with a semicolon (;)
- **If user already exists**: Drop the user first with `DROP USER IF EXISTS attendance_user;`
- **If you make a typo**: Complete the command with `;` then run the correct command
- **Console encoding warnings**: These are normal and won't affect functionality

#### Initialize Database Schema

```bash
# Navigate to database directory
cd database

# Run initialization script
python init_db.py

# Verify schema creation
psql -U attendance_user -d attendance_system -c "\dt"
```

### 2. Sample Data Setup (Optional)

```bash
# Load sample data for testing
python load_sample_data.py
```

---

## Configuration

### 1. Environment Variables

Create `.env` file in the backend directory:

```env
# Database Configuration
DATABASE_URL=postgresql://attendance_user:your_secure_password@localhost:5432/attendance_system

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your_very_secure_secret_key_here

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ACCESS_TOKEN_EXPIRES=3600

# Face Recognition Settings
FACE_RECOGNITION_TOLERANCE=0.6
FACE_RECOGNITION_MODEL=hog

# File Upload Settings
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Power BI Configuration
POWERBI_CLIENT_ID=your_powerbi_client_id
POWERBI_CLIENT_SECRET=your_powerbi_client_secret
POWERBI_TENANT_ID=your_powerbi_tenant_id

# Email Configuration (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@domain.com
MAIL_PASSWORD=your_app_password

# Security Settings
ENCRYPTION_KEY=your_32_character_encryption_key
BCRYPT_LOG_ROUNDS=12
SESSION_TIMEOUT=1800
```

### 2. Application Configuration

Update `config/settings.json`:

```json
{
  "app": {
    "name": "Automated Attendance System",
    "version": "1.0.0",
    "debug": false,
    "host": "0.0.0.0",
    "port": 5000
  },
  "face_recognition": {
    "tolerance": 0.6,
    "model": "hog",
    "num_jitters": 1,
    "recognition_threshold": 0.4
  },
  "attendance": {
    "auto_mark_present": true,
    "late_threshold_minutes": 15,
    "early_departure_threshold_minutes": 30
  },
  "backup": {
    "enabled": true,
    "frequency": "daily",
    "retention_days": 30,
    "backup_path": "/var/backups/attendance"
  },
  "logging": {
    "level": "INFO",
    "file_path": "logs/app.log",
    "max_file_size": "10MB",
    "backup_count": 5
  }
}
```

---

## Deployment Options

### Option 1: Single Server Deployment

#### Using Gunicorn and Nginx

1. **Install Gunicorn**
```bash
pip install gunicorn
```

2. **Create Gunicorn Configuration**
```python
# gunicorn.conf.py
bind = "127.0.0.1:5000"
workers = 4
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
```

3. **Nginx Configuration**
```nginx
# /etc/nginx/sites-available/attendance-system
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 50M;
    }
}
```

4. **Enable Nginx Site**
```bash
sudo ln -s /etc/nginx/sites-available/attendance-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Option 2: Docker Deployment

#### Create Dockerfile for Backend

```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer1.0-0 \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
```

#### Create Dockerfile for Frontend

```dockerfile
# frontend/Dockerfile
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: attendance_system
      POSTGRES_USER: attendance_user
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/schema.sql:/docker-entrypoint-initdb.d/schema.sql
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://attendance_user:your_secure_password@postgres:5432/attendance_system
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./uploads:/app/uploads
    ports:
      - "5000:5000"

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

#### Deploy with Docker

```bash
# Build and start services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

---

## Security Configuration

### 1. SSL/TLS Setup

#### Let's Encrypt with Certbot

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal setup
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 5432/tcp  # Block external PostgreSQL access
```

### 3. Database Security

```sql
-- Create read-only user for reports
CREATE USER report_user WITH PASSWORD 'report_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO report_user;

-- Configure connection limits
ALTER USER attendance_user CONNECTION LIMIT 50;
```

---

## Maintenance and Updates

### 1. Backup Procedures

#### Automated Database Backup

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/attendance"
DB_NAME="attendance_system"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -U attendance_user -h localhost $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# File backup
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz uploads/

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

#### Schedule Backups

```bash
# Add to crontab
sudo crontab -e

# Daily backup at 2 AM
0 2 * * * /path/to/backup.sh
```

### 2. Update Procedures

#### Application Updates

```bash
# 1. Backup current installation
./backup.sh

# 2. Stop services
sudo systemctl stop attendance-backend
sudo systemctl stop nginx

# 3. Update code
git pull origin main

# 4. Update dependencies
pip install -r backend/requirements.txt
cd frontend && npm install && npm run build

# 5. Run database migrations (if any)
python database/migrate.py

# 6. Restart services
sudo systemctl start attendance-backend
sudo systemctl start nginx

# 7. Verify deployment
curl -f http://localhost/api/health
```

### 3. Log Monitoring

```bash
# Monitor application logs
tail -f logs/app.log

# Monitor system logs
sudo journalctl -u attendance-backend -f

# Check Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Face Recognition Performance Issues

**Problem**: Slow face recognition or high CPU usage

**Solutions**:
```python
# Optimize face_recognition settings
FACE_RECOGNITION_MODEL = "hog"  # Use HOG instead of CNN for CPU
FACE_RECOGNITION_TOLERANCE = 0.6  # Adjust tolerance
NUM_JITTERS = 1  # Reduce for speed, increase for accuracy
```

#### 2. Database Connection Issues

**Problem**: Database connection errors

**Solutions**:
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -U attendance_user -d attendance_system -c "SELECT 1;"

# Check connection limits
psql -U postgres -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
```

#### 3. Memory Issues

**Problem**: High memory usage or out-of-memory errors

**Solutions**:
```python
# Add to application configuration
FACE_ENCODINGS_CACHE_SIZE = 1000  # Limit cache size
PROCESS_FRAME_INTERVAL = 5  # Process every 5th frame
```

#### 4. Camera Access Issues

**Problem**: Browser cannot access camera

**Solutions**:
- Ensure HTTPS is enabled (required for camera access)
- Check browser permissions
- Verify camera is not being used by another application

#### 5. NPM Dependency Conflicts

**Problem**: npm install fails with ERESOLVE unable to resolve dependency tree

**Solutions**:
```bash
# Try installing with legacy peer deps
npm install --legacy-peer-deps

# Or force the installation
npm install --force

# Clear npm cache if needed
npm cache clean --force
npm install --legacy-peer-deps
```

**Alternative Solution**:
```bash
# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

#### 6. PostgreSQL Command Not Found (Windows)

**Problem**: `psql` command not recognized on Windows

**Solutions**:
```powershell
# Option 1: Add PostgreSQL to PATH temporarily
$env:PATH += ";C:\Program Files\PostgreSQL\14\bin"
psql -U postgres -h localhost

# Option 2: Use full path to psql
& "C:\Program Files\PostgreSQL\14\bin\psql.exe" -U postgres -h localhost

# Option 3: Use pgAdmin GUI instead
# Open pgAdmin (installed with PostgreSQL) and create database through GUI
```

**Alternative Database Setup for Windows**:
If PostgreSQL command line is not working, you can:
1. Open **pgAdmin** (installed with PostgreSQL)
2. Connect to local server using your postgres password
3. Right-click "Databases" → Create → Database
4. Name: `attendance_system`
5. Right-click "Login/Group Roles" → Create → Login/Group Role
6. Name: `attendance_user`, set password, grant privileges

### Performance Monitoring

#### Setup System Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop netstat

# Monitor system resources
htop

# Monitor network connections
netstat -tulpn | grep :5000

# Check disk usage
df -h
```

#### Application Performance Metrics

```python
# Add to Flask app for monitoring
from flask import Flask, jsonify
import psutil

@app.route('/api/system-status')
def system_status():
    return jsonify({
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent
    })
```

---

## Production Checklist

### Pre-Deployment Checklist

- [ ] All environment variables configured
- [ ] Database schema initialized
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] Backup procedures tested
- [ ] Log rotation configured
- [ ] Monitoring tools installed
- [ ] Performance testing completed
- [ ] Security audit performed
- [ ] Documentation updated

### Post-Deployment Verification

```bash
# Test all endpoints
curl -f http://your-domain.com/api/health
curl -f http://your-domain.com/api/users/current

# Verify database connections
psql -U attendance_user -d attendance_system -c "SELECT COUNT(*) FROM users;"

# Check log files
tail -f logs/app.log

# Monitor system resources
htop
```

---

*This installation guide is version 1.0 - Last updated: October 2025*
*For technical support, contact: tech-support@attendance-system.com*