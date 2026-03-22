# Automated Attendance System for Rural Schools

A comprehensive facial recognition-based attendance system designed specifically for rural schools, featuring offline capabilities, Power BI integration, and user-friendly interfaces.

## 🎯 Project Overview

The Automated Attendance System leverages modern facial recognition technology to:
- Automate student attendance tracking
- Provide real-time analytics and dashboards
- Support offline-first architecture for rural connectivity
- Ensure security and prevent fraudulent attendance
- Integrate with Power BI for advanced reporting

## 🚀 Features

### Core Functionality
- **Facial Recognition**: Real-time student identification with 95%+ accuracy
- **Student Registration**: Easy enrollment with demographic data and facial capture
- **Attendance Tracking**: Automatic marking with duplicate prevention
- **Dashboard**: Comprehensive view of attendance records and analytics
- **Reporting**: Export capabilities and Power BI integration

### Technical Features
- **Offline Support**: Works without internet with auto-sync capability
- **Security**: Encrypted data storage and role-based access control
- **Scalability**: Single classroom to multi-school deployment
- **Performance**: Sub-2-second processing time per student
- **Compatibility**: Web-based system accessible on PC, laptop, tablet

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (React)       │◄──►│   (Python)      │◄──►│ (PostgreSQL)    │
│                 │    │                 │    │                 │
│ • Dashboard     │    │ • Face Recog.   │    │ • Students      │
│ • Registration  │    │ • API Endpoints │    │ • Attendance    │
│ • Reports       │    │ • Auth System   │    │ • Users         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Power BI      │
                       │   Integration   │
                       │                 │
                       │ • Dashboards    │
                       │ • Analytics     │
                       │ • Reports       │
                       └─────────────────┘
```

## 📋 Requirements

### Hardware Requirements
- **Camera**: HD camera (minimum 720p, 30fps)
- **Server**: Quad-Core 2.5GHz, 8GB RAM, 500GB storage
- **Client**: PC/Laptop with modern web browser

### Software Dependencies
- Python 3.8+
- Node.js 14+
- PostgreSQL 12+
- OpenCV
- Face Recognition Library
- React 18+

## 🛠️ Installation

### Backend Setup
1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure database (Flask/SQLAlchemy):
   Create a `.env` file in `backend/` and set your configuration. For local SQLite use:
   
   ```
   # backend/.env
   SECRET_KEY=change-me
   JWT_SECRET_KEY=change-me-too
   DATABASE_URL=sqlite:///instance/attendance_system.db
   ```

   Initialize the database:
   - Option A (SQLite/local): Run the app once to auto-create tables
     ```
     python app.py
     ```
     Then stop it (Ctrl+C) if you wish to run via a different method.

   - Option B (PostgreSQL): Create a database and set `DATABASE_URL` accordingly, then apply the schema in `database/schema.sql` or run the helper in `database/setup_db.py`.

5. Start server:
   ```bash
   python app.py
   ```

### Frontend Setup
1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies (use --legacy-peer-deps for compatibility):
   ```bash
   npm install --legacy-peer-deps
   ```

3. Start development server:
   ```bash
   npm start
   ```

## 📖 Usage

### Student Registration
1. Access the registration module
2. Enter student details (Name, Roll No., Class, etc.)
3. Capture facial images for recognition
4. Save student profile

### Daily Attendance
1. Position camera at classroom entrance
2. Students enter naturally - system detects faces automatically
3. Real-time attendance marking with visual feedback
4. Review and approve attendance records

### Reporting & Analytics
1. Access dashboard for attendance overview
2. Generate reports by date, class, or student
3. Export data to Excel/PDF
4. View Power BI dashboards for advanced analytics

## 👥 User Roles

- **Administrator**: Full system access, user management, system configuration
- **Teacher**: Attendance management, student records, basic reports
- **Principal**: Analytics access, advanced reports, oversight functions

## 🔧 Configuration

Key configuration files:
- `config/settings.json`: Database and system settings
- `config/face_recognition.json`: Recognition parameters
- `config/powerbi.json`: Power BI integration settings

## 📊 Power BI Integration

The system automatically exports attendance data for Power BI visualization:
- Daily attendance rates
- Student attendance trends
- Class-wise performance
- Irregular attendance alerts
- Monthly/yearly analytics

## 🔒 Security Features

- Encrypted facial data storage
- Role-based access control
- Audit logging for all actions
- Secure API endpoints
- Data privacy compliance

## 🌐 Offline Mode

- Local data storage during connectivity issues
- Automatic synchronization when online
- Conflict resolution mechanisms
- Battery backup considerations

## 📚 Documentation

- [User Manual](docs/user-manual.md)
- [Administrator Guide](docs/admin-guide.md)
- [API Documentation](docs/api-documentation.md)
- [Deployment Guide](docs/deployment-guide.md)

## 🤝 Support

For technical support or questions:
- Email: support@attendance-system.com
- Documentation: [docs/](docs/)
- Issues: Create a GitHub issue

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenCV community for computer vision tools
- Face Recognition library contributors
- Rural education initiatives for requirements gathering

---
**Version**: 1.0.0  
**Last Updated**: October 2025  
**Compatibility**: Windows, Linux, macOS