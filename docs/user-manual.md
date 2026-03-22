# User Manual - Automated Attendance System for Rural Schools

## Table of Contents
1. [Getting Started](#getting-started)
2. [User Roles and Permissions](#user-roles-and-permissions)
3. [Student Management](#student-management)
4. [Attendance Tracking](#attendance-tracking)
5. [Reports and Analytics](#reports-and-analytics)
6. [System Settings](#system-settings)
7. [Troubleshooting](#troubleshooting)
8. [Frequently Asked Questions](#frequently-asked-questions)

---

## Getting Started

### System Requirements
- **Web Browser**: Chrome 90+, Firefox 85+, Safari 14+, or Edge 90+
- **Camera**: HD webcam (minimum 720p resolution)
- **Internet**: Stable connection (system works offline with limited functionality)
- **Screen Resolution**: Minimum 1024x768

### First Login
1. Open your web browser and navigate to the attendance system URL
2. Use the provided credentials to log in:
   - **Administrator**: Username: `admin`, Password: `admin123`
   - **Teacher**: Username: `teacher1`, Password: `teacher123`
3. Change your password immediately after first login

### Dashboard Overview
After logging in, you'll see the main dashboard with:
- **Statistics Cards**: Total students, present today, attendance rate, alerts
- **Quick Actions**: Navigation to different system features
- **System Status**: Current system health indicators

---

## User Roles and Permissions

### Administrator
**Full system access including:**
- User management (create, edit, delete users)
- System configuration and settings
- Complete student and attendance data access
- Report generation and export
- Power BI integration management
- Audit log access

### Teacher
**Standard teaching functionality:**
- View assigned class students
- Mark and modify attendance
- Generate class reports
- Register new students (if permitted)
- View attendance analytics for their classes

### Principal
**Oversight and reporting access:**
- View all student and attendance data
- Generate comprehensive reports
- Access analytics and dashboards
- Monitor system usage
- Limited user management

---

## Student Management

### Adding New Students

1. **Navigate to Students Page**
   - Click "Students" in the sidebar menu

2. **Add Student Information**
   - Click "Add New Student" button
   - Fill in required fields:
     - Roll Number (unique identifier)
     - Admission Number (unique identifier)
     - Full Name
     - Class and Section
     - Date of Birth (optional)
     - Parent Contact Information

3. **Register Face for Recognition**
   - After saving student details, click "Register Face"
   - Ensure good lighting and clear face visibility
   - Capture 3-5 different angles of the student's face
   - System will validate face quality automatically

### Best Practices for Face Registration

**Lighting Requirements:**
- Use natural daylight or bright indoor lighting
- Avoid harsh shadows on the face
- Ensure even illumination

**Face Position:**
- Student should look directly at camera
- Capture slight variations (left turn, right turn, straight)
- Maintain 2-3 feet distance from camera
- Avoid obstructions (glasses glare, hair covering face)

**Photo Quality:**
- Minimum 200x200 pixel face size
- Clear, sharp images (avoid motion blur)
- Neutral expression preferred
- Multiple angles improve recognition accuracy

### Editing Student Information

1. Find student in the list using search or filters
2. Click "Edit" button next to student name
3. Modify required information
4. Save changes
5. Re-register face if needed for better accuracy

---

## Attendance Tracking

### Real-Time Facial Recognition

1. **Setup Camera**
   - Navigate to "Attendance" page
   - Click "Start Camera" to begin live feed
   - Position camera at classroom entrance
   - Ensure good lighting conditions

2. **Automatic Recognition**
   - Students walk naturally in front of camera
   - System automatically detects and recognizes faces
   - Attendance is marked in real-time
   - Recognition results appear on screen immediately

3. **Manual Corrections**
   - Review attendance list after automated marking
   - Manually mark absent students as present if needed
   - Add notes for late arrivals or early departures
   - Correct any misidentifications

### Daily Attendance Process

**Morning Routine:**
1. Start the attendance system camera
2. Allow students to enter classroom naturally
3. Monitor recognition results on screen
4. Handle any unrecognized students manually
5. Review and confirm final attendance list

**End of Day:**
1. Mark any additional late arrivals
2. Record early departures if applicable
3. Add notes for excused absences
4. Generate daily attendance report

### Handling Special Cases

**New Students:**
- Manually mark attendance until face registration is complete
- Register face during break time for future recognition

**Recognition Issues:**
- Check lighting conditions
- Clean camera lens
- Re-register student face if consistently failing
- Use manual override when needed

**Multiple Students:**
- System can handle up to 50 students simultaneously
- Ensure students don't crowd in front of camera
- Allow natural flow of entry

---

## Reports and Analytics

### Daily Reports

1. **Generate Daily Attendance**
   - Select date from calendar
   - Choose class/section filters
   - Click "Generate Report"
   - Review attendance statistics

2. **Export Options**
   - PDF format for printing
   - Excel format for data analysis
   - CSV format for external systems

### Monthly Analytics

**Attendance Trends:**
- View monthly attendance percentages
- Identify patterns and irregularities
- Track improvement over time

**Student Performance:**
- Individual student attendance rates
- Identify students needing attention
- Generate parent communication reports

### Power BI Integration

**Dashboard Access:**
1. Click "View Power BI Dashboard" in Reports section
2. Interactive charts and graphs
3. Real-time data synchronization
4. Advanced filtering and drill-down capabilities

**Key Metrics:**
- Overall attendance trends
- Class-wise performance comparison
- Student attendance rankings
- Alert notifications for concerning patterns

---

## System Settings

*Note: Settings access requires Administrator role*

### Face Recognition Configuration

**Recognition Parameters:**
- Tolerance Level: Adjust recognition sensitivity
- Confidence Threshold: Set minimum confidence for matches
- Processing Interval: Configure recognition frequency

**Camera Settings:**
- Resolution configuration
- Frame rate settings
- Multiple camera support

### User Management

**Adding Users:**
1. Navigate to Settings → Users
2. Click "Add New User"
3. Assign appropriate role (Teacher, Admin, Principal)
4. Set initial password (user must change on first login)

**Role Permissions:**
- Customize permissions per role
- Enable/disable specific features
- Set data access levels

### System Maintenance

**Data Backup:**
- Schedule automatic backups
- Export student and attendance data
- Verify backup integrity regularly

**Performance Monitoring:**
- Monitor system resources
- Track recognition accuracy
- Review error logs

---

## Troubleshooting

### Common Issues and Solutions

#### Camera Not Working
**Problem:** Camera feed not displaying
**Solutions:**
- Check camera connection
- Allow camera permissions in browser
- Refresh the page and try again
- Check if camera is being used by another application

#### Face Recognition Not Working
**Problem:** System not recognizing registered students
**Solutions:**
- Verify lighting conditions (bright, even lighting)
- Check camera focus and cleanliness
- Re-register student faces with better quality images
- Adjust recognition tolerance in settings

#### Slow Performance
**Problem:** System running slowly
**Solutions:**
- Close unnecessary browser tabs
- Check internet connection speed
- Clear browser cache and cookies
- Restart the browser

#### Login Issues
**Problem:** Cannot log into the system
**Solutions:**
- Verify username and password
- Check for caps lock
- Contact administrator for password reset
- Clear browser cache

#### Data Not Syncing
**Problem:** Attendance data not saving properly
**Solutions:**
- Check internet connection
- Wait for automatic sync (offline mode)
- Manually sync when connection restored
- Contact technical support if persistent

### Getting Help

**Contact Information:**
- Technical Support: support@attendance-system.com
- User Documentation: Available in system Help section
- Training Videos: Accessible through user dashboard
- Administrator Manual: Separate document for system admins

**Emergency Procedures:**
- Manual attendance backup sheets available
- Offline mode continues basic functionality
- Contact IT support for system outages
- Use mobile app (if available) as backup

---

## Frequently Asked Questions

### General Questions

**Q: How accurate is the facial recognition?**
A: The system achieves 95%+ accuracy under proper conditions with well-registered faces and good lighting.

**Q: Can the system work without internet?**
A: Yes, the system has offline capabilities. Data syncs automatically when connection is restored.

**Q: How many students can be recognized at once?**
A: The system can handle up to 50 students entering simultaneously.

### Technical Questions

**Q: What happens if a student's face changes (haircut, glasses)?**
A: You may need to re-register their face or add additional face samples for continued accuracy.

**Q: Can parents access attendance information?**
A: This depends on system configuration. Administrators can enable parent access modules.

**Q: How is student data protected?**
A: All data is encrypted and stored securely. The system follows privacy regulations and data protection standards.

### Usage Questions

**Q: What should I do if the camera stops working during class?**
A: Switch to manual attendance marking. The system allows manual entry for all students.

**Q: How often should face data be updated?**
A: Re-register faces if recognition accuracy decreases, typically every 6-12 months or after significant appearance changes.

**Q: Can I mark attendance for past dates?**
A: Yes, users with appropriate permissions can mark attendance for previous dates with proper authorization.

---

## Quick Reference Card

### Daily Checklist
- [ ] Start camera system
- [ ] Check lighting conditions
- [ ] Monitor recognition results
- [ ] Handle unrecognized students
- [ ] Review final attendance
- [ ] Generate daily report

### Keyboard Shortcuts
- `Ctrl + D`: Open Dashboard
- `Ctrl + S`: Save current data
- `Ctrl + P`: Print current report
- `F5`: Refresh camera feed
- `Esc`: Cancel current operation

### Emergency Contacts
- Technical Support: [Phone Number]
- System Administrator: [Phone Number]
- IT Helpdesk: [Email Address]

---

*This manual is version 1.0 - Last updated: October 2025*
*For the latest version and updates, visit the system documentation portal*