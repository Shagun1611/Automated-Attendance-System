#!/usr/bin/env python3
"""
Demo script showing how to add students and mark attendance
"""

import requests
import json
from datetime import datetime, date

# API Base URL
API_BASE = "http://127.0.0.1:5000/api"
#login credentials
def login():
    """Login and get access token"""
    login_url = f"{API_BASE}/auth/login"
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    print("🔐 Logging in...")
    response = requests.post(login_url, json=login_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Login successful! Welcome {result['user']['full_name']}")
        return result['access_token']
    else:
        print(f"❌ Login failed: {response.json()}")
        return None

def add_student(access_token, student_data):
    """Add a new student"""
    url = f"{API_BASE}/students"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n👤 Adding student: {student_data['full_name']}")
    response = requests.post(url, json=student_data, headers=headers)
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Student added successfully!")
        print(f"   - ID: {result['student']['id']}")
        print(f"   - Roll Number: {result['student']['roll_number']}")
        print(f"   - Class: {result['student']['class_name']} - {result['student']['section']}")
        return result['student']
    else:
        print(f"❌ Failed to add student: {response.json()}")
        return None

def mark_attendance(access_token, student_id, attendance_date=None, status="present"):
    """Mark attendance for a student"""
    url = f"{API_BASE}/attendance/manual"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    if not attendance_date:
        attendance_date = date.today().strftime('%Y-%m-%d')
    
    attendance_data = {
        "student_id": student_id,
        "date": attendance_date,
        "status": status,
        "time_in": datetime.now().strftime('%H:%M'),
        "notes": f"Manually marked as {status}"
    }
    
    print(f"\n📝 Marking attendance for Student ID {student_id}...")
    response = requests.post(url, json=attendance_data, headers=headers)
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Attendance marked successfully!")
        print(f"   - Student: {result['attendance']['student_name']}")
        print(f"   - Date: {result['attendance']['date']}")
        print(f"   - Status: {result['attendance']['status']}")
        print(f"   - Time: {result['attendance']['time_in']}")
        return result['attendance']
    else:
        print(f"❌ Failed to mark attendance: {response.json()}")
        return None

def get_students(access_token, class_name=None):
    """Get list of students"""
    url = f"{API_BASE}/students"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    params = {}
    if class_name:
        params['class'] = class_name
    
    print(f"\n📋 Getting students list...")
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {result['count']} students")
        for student in result['students']:
            print(f"   - {student['full_name']} (ID: {student['id']}, Roll: {student['roll_number']})")
        return result['students']
    else:
        print(f"❌ Failed to get students: {response.json()}")
        return []

def get_attendance_by_date(access_token, date_str=None):
    """Get attendance for a specific date"""
    if not date_str:
        date_str = date.today().strftime('%Y-%m-%d')
    
    url = f"{API_BASE}/attendance/date/{date_str}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print(f"\n📅 Getting attendance for {date_str}...")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {result['count']} attendance records")
        for record in result['attendance']:
            print(f"   - {record['student_name']}: {record['status']} at {record['time_in']}")
        return result['attendance']
    else:
        print(f"❌ Failed to get attendance: {response.json()}")
        return []

def main():
    """Main demonstration function"""
    print("🎓 Automated Attendance System Demo")
    print("=" * 50)
    
    # Step 1: Login
    access_token = login()
    if not access_token:
        return
    
    # Step 2: Add sample students
    sample_students = [
        {
            "roll_number": "2024001",
            "admission_number": "ADM001",
            "full_name": "Alice Johnson",
            "class_name": "Grade 5",
            "section": "A",
            "date_of_birth": "2014-05-15",
            "parent_contact": "+1234567890",
            "parent_email": "alice.parent@email.com"
        },
        {
            "roll_number": "2024002",
            "admission_number": "ADM002",
            "full_name": "Bob Smith",
            "class_name": "Grade 5",
            "section": "A",
            "date_of_birth": "2014-08-22",
            "parent_contact": "+1234567891",
            "parent_email": "bob.parent@email.com"
        },
        {
            "roll_number": "2024003",
            "admission_number": "ADM003",
            "full_name": "Carol Davis",
            "class_name": "Grade 6",
            "section": "B",
            "date_of_birth": "2013-12-03",
            "parent_contact": "+1234567892",
            "parent_email": "carol.parent@email.com"
        }
    ]
    
    added_students = []
    for student_data in sample_students:
        student = add_student(access_token, student_data)
        if student:
            added_students.append(student)
    
    # Step 3: Show all students
    all_students = get_students(access_token)
    
    # Step 4: Mark attendance for added students
    today = date.today().strftime('%Y-%m-%d')
    for student in added_students:
        mark_attendance(access_token, student['id'], today, "present")
    
    # Step 5: Show today's attendance
    get_attendance_by_date(access_token, today)
    
    print("\n🎉 Demo completed successfully!")
    print("\nWhat you learned:")
    print("1. How to login and get access token")
    print("2. How to add students to the system")
    print("3. How to mark attendance manually")
    print("4. How to view students and attendance records")

if __name__ == '__main__':
    main()