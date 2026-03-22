# 📚 How to Add Students and Mark Attendance

## 🔐 Prerequisites
- Flask backend server running on `http://127.0.0.1:5000`
- Admin credentials: username=`admin`, password=`admin123`

## 📋 Step-by-Step Guide

### 1. **Login to Get Access Token**

**API Endpoint:** `POST /api/auth/login`

**Request:**
```json
{
    "username": "admin",
    "password": "admin123"
}
```

**Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 1,
        "username": "admin",
        "role": "admin",
        "full_name": "System Administrator"
    },
    "message": "Login successful"
}
```

**PowerShell Example:**
```powershell
$headers = @{'Content-Type' = 'application/json'}
$body = '{"username": "admin", "password": "admin123"}'
$response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/auth/login" -Method POST -Body $body -Headers $headers
$token = $response.access_token
```

---

### 2. **Add a New Student**

**API Endpoint:** `POST /api/students`

**Required Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
    "roll_number": "2024001",
    "admission_number": "ADM001",
    "full_name": "Alice Johnson",
    "class_name": "Grade 5",
    "section": "A",
    "date_of_birth": "2014-05-15",
    "parent_contact": "+1234567890",
    "parent_email": "alice.parent@email.com",
    "address": "123 Main Street, City"
}
```

**PowerShell Example:**
```powershell
$headers = @{
    'Authorization' = "Bearer $token"
    'Content-Type' = 'application/json'
}
$studentData = @{
    roll_number = "2024001"
    admission_number = "ADM001"
    full_name = "Alice Johnson"
    class_name = "Grade 5"
    section = "A"
    date_of_birth = "2014-05-15"
    parent_contact = "+1234567890"
    parent_email = "alice.parent@email.com"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/students" -Method POST -Body $studentData -Headers $headers
```

---

### 3. **View All Students**

**API Endpoint:** `GET /api/students`

**Optional Query Parameters:**
- `class`: Filter by class name
- `section`: Filter by section
- `search`: Search by name, roll number, or admission number

**PowerShell Example:**
```powershell
$headers = @{'Authorization' = "Bearer $token"}
$students = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/students" -Method GET -Headers $headers
$students.students | Format-Table id, full_name, roll_number, class_name, section
```

---

### 4. **Mark Attendance Manually**

**API Endpoint:** `POST /api/attendance/manual`

**Request Body:**
```json
{
    "student_id": 1,
    "date": "2025-10-03",
    "status": "present",
    "time_in": "08:30",
    "notes": "Manually marked present"
}
```

**Status Options:**
- `"present"` - Student is present
- `"absent"` - Student is absent  
- `"late"` - Student is late

**PowerShell Example:**
```powershell
$headers = @{
    'Authorization' = "Bearer $token"
    'Content-Type' = 'application/json'
}
$attendanceData = @{
    student_id = 1
    date = "2025-10-03"
    status = "present"
    time_in = "08:30"
    notes = "Present on time"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/attendance/manual" -Method POST -Body $attendanceData -Headers $headers
```

---

### 5. **View Attendance by Date**

**API Endpoint:** `GET /api/attendance/date/{date}`

**PowerShell Example:**
```powershell
$headers = @{'Authorization' = "Bearer $token"}
$date = "2025-10-03"
$attendance = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/attendance/date/$date" -Method GET -Headers $headers
$attendance.attendance | Format-Table student_name, status, time_in, marked_by
```

---

### 6. **View Student Attendance History**

**API Endpoint:** `GET /api/attendance/student/{student_id}`

**Optional Query Parameters:**
- `start_date`: Filter from this date (YYYY-MM-DD)
- `end_date`: Filter to this date (YYYY-MM-DD)

**PowerShell Example:**
```powershell
$headers = @{'Authorization' = "Bearer $token"}
$studentId = 1
$history = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/attendance/student/$studentId" -Method GET -Headers $headers
$history.attendance_history | Format-Table date, status, time_in, marked_by
```

---

## 🎯 Quick Start Script

Save this as `quick_add_student.ps1`:

```powershell
# Login
$loginBody = '{"username": "admin", "password": "admin123"}'
$loginHeaders = @{'Content-Type' = 'application/json'}
$loginResponse = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/auth/login" -Method POST -Body $loginBody -Headers $loginHeaders
$token = $loginResponse.access_token
Write-Host "✅ Logged in successfully!"

# Add Student
$studentData = @{
    roll_number = "2024004"
    admission_number = "ADM004"
    full_name = "David Wilson"
    class_name = "Grade 7"
    section = "A"
    date_of_birth = "2012-03-10"
    parent_contact = "+1234567893"
    parent_email = "david.parent@email.com"
} | ConvertTo-Json

$studentHeaders = @{
    'Authorization' = "Bearer $token"
    'Content-Type' = 'application/json'
}
$studentResponse = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/students" -Method POST -Body $studentData -Headers $studentHeaders
$studentId = $studentResponse.student.id
Write-Host "✅ Student added with ID: $studentId"

# Mark Attendance
$attendanceData = @{
    student_id = $studentId
    date = (Get-Date -Format "yyyy-MM-dd")
    status = "present"
    time_in = (Get-Date -Format "HH:mm")
    notes = "Added via PowerShell script"
} | ConvertTo-Json

$attendanceResponse = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/attendance/manual" -Method POST -Body $attendanceData -Headers $studentHeaders
Write-Host "✅ Attendance marked successfully!"
```

---

## 🌐 Using the Web Interface

1. **Open:** `http://localhost:3000` in your browser
2. **Login:** Use `admin` / `admin123`
3. **Navigate to Students:** Add students through the web form
4. **Mark Attendance:** Use the attendance marking interface

---

## 📱 Mobile/Camera Integration

For **face recognition attendance**, you would:

1. **Register Face:** Upload student photos via `/api/students/{id}/register-face`
2. **Live Recognition:** Send camera frames to `/api/attendance/recognize`
3. **Auto-Mark:** System automatically marks attendance when faces are detected

---

## 🔍 Tips & Best Practices

1. **Unique Identifiers:** Always use unique roll numbers and admission numbers
2. **Date Format:** Use YYYY-MM-DD for dates
3. **Time Format:** Use HH:MM for times (24-hour format)
4. **Status Values:** Use "present", "absent", or "late"
5. **Authentication:** Include Bearer token in all requests after login
6. **Error Handling:** Check response status codes and error messages

---

## 🚀 Available API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login and get access token |
| GET | `/api/students` | Get all students |
| POST | `/api/students` | Add new student |
| POST | `/api/attendance/manual` | Mark attendance manually |
| GET | `/api/attendance/date/{date}` | Get attendance by date |
| GET | `/api/attendance/student/{id}` | Get student attendance history |

**Your system is now ready for student management and attendance tracking!** 🎉