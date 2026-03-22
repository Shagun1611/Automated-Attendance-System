from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from werkzeug.utils import secure_filename
from app import app, db
from app.models import User, Student, AttendanceRecord, Class, AuditLog
import json
from app.services.face_recognition_service import FaceRecognitionService
from app.services.attendance_service import AttendanceService
from datetime import datetime, date
import os
import logging

# Initialize services
face_service = FaceRecognitionService()
attendance_service = AttendanceService()

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User authentication endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            access_token = create_access_token(identity=user.id)
            return jsonify({
                'access_token': access_token,
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/students', methods=['GET'])
@jwt_required()
def get_students():
    """Get all students"""
    try:
        class_name = request.args.get('class')
        section = request.args.get('section')
        search = request.args.get('search')
        
        query = Student.query.filter_by(is_active=True)
        
        if class_name:
            query = query.filter(Student.class_name == class_name)
        
        if section:
            query = query.filter(Student.section == section)
        
        if search:
            query = query.filter(
                Student.full_name.contains(search) | 
                Student.roll_number.contains(search) |
                Student.admission_number.contains(search)
            )
        
        students = query.all()
        students_data = [student.to_dict() for student in students]
        
        return jsonify({'students': students_data}), 200
    
    except Exception as e:
        logging.error(f"Get students error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/students', methods=['POST'])
@jwt_required()
def create_student():
    """Create new student"""
    try:
        data = request.get_json()
        
        # Check if student already exists
        existing_student = Student.query.filter(
            (Student.roll_number == data.get('roll_number')) |
            (Student.admission_number == data.get('admission_number'))
        ).first()
        
        if existing_student:
            return jsonify({'error': 'Student with this roll number or admission number already exists'}), 400
        
        # Create new student
        student = Student(
            roll_number=data.get('roll_number'),
            admission_number=data.get('admission_number'),
            full_name=data.get('full_name'),
            class_name=data.get('class_name'),
            section=data.get('section'),
            date_of_birth=datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date() if data.get('date_of_birth') else None,
            parent_contact=data.get('parent_contact'),
            parent_email=data.get('parent_email'),
            address=data.get('address')
        )
        
        db.session.add(student)
        db.session.commit()
        
        return jsonify({
            'message': 'Student created successfully',
            'student': student.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"Create student error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/students/<int:student_id>/register-face', methods=['POST'])
@jwt_required()
def register_student_face(student_id):
    """Register face for student"""
    try:
        if 'images' not in request.files:
            return jsonify({'error': 'No images provided'}), 400
        
        files = request.files.getlist('images')
        if not files or len(files) == 0:
            return jsonify({'error': 'No images provided'}), 400
        
        # Save uploaded images
        image_paths = []
        for file in files:
            if file and file.filename:
                filename = secure_filename(f"{student_id}_{datetime.now().timestamp()}_{file.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_paths.append(filepath)
        
        # Register faces
        success, message = face_service.register_student_faces(student_id, image_paths)
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
    
    except Exception as e:
        logging.error(f"Register face error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/attendance/recognize', methods=['POST'])
@jwt_required()
def recognize_and_mark_attendance():
    """Recognize faces and mark attendance"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        if not file or not file.filename:
            return jsonify({'error': 'Invalid image file'}), 400
        
        # Save temporary image
        filename = secure_filename(f"temp_{datetime.now().timestamp()}_{file.filename}")
        temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        # Recognize faces
        success, recognized_faces = face_service.recognize_faces(temp_path)
        
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if not success:
            return jsonify({'error': recognized_faces}), 400
        
        # Mark attendance for recognized students
        attendance_results = []
        for face in recognized_faces:
            if face['confidence'] >= 0.6:  # Minimum confidence threshold
                success, message = attendance_service.mark_attendance(
                    face['student_id'],
                    face['confidence']
                )
                attendance_results.append({
                    'student_id': face['student_id'],
                    'student_name': face['student_name'],
                    'confidence': face['confidence'],
                    'success': success,
                    'message': message
                })
        
        return jsonify({
            'recognized_faces': recognized_faces,
            'attendance_results': attendance_results
        }), 200
    
    except Exception as e:
        logging.error(f"Recognize attendance error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/attendance/date/<string:date_str>', methods=['GET'])
@jwt_required()
def get_attendance_by_date(date_str):
    """Get attendance records for specific date"""
    try:
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        class_name = request.args.get('class')
        section = request.args.get('section')
        
        success, attendance_data = attendance_service.get_attendance_by_date(
            attendance_date, class_name, section
        )
        
        if success:
            return jsonify({'attendance': attendance_data}), 200
        else:
            return jsonify({'error': attendance_data}), 400
    
    except Exception as e:
        logging.error(f"Get attendance by date error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/attendance/student/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_attendance_history(student_id):
    """Get attendance history for specific student"""
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        
        success, attendance_history = attendance_service.get_student_attendance_history(
            student_id, start_date, end_date
        )
        
        if success:
            return jsonify({'attendance_history': attendance_history}), 200
        else:
            return jsonify({'error': attendance_history}), 400
    
    except Exception as e:
        logging.error(f"Get student attendance history error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/attendance/statistics', methods=['GET'])
@jwt_required()
def get_attendance_statistics():
    """Get attendance statistics"""
    try:
        class_name = request.args.get('class')
        section = request.args.get('section')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        
        success, statistics = attendance_service.get_attendance_statistics(
            class_name, section, start_date, end_date
        )
        
        if success:
            return jsonify({'statistics': statistics}), 200
        else:
            return jsonify({'error': statistics}), 400
    
    except Exception as e:
        logging.error(f"Get attendance statistics error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/attendance/manual', methods=['POST'])
@jwt_required()
def mark_manual_attendance():
    """Manually mark attendance"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        student_id = data.get('student_id')
        attendance_date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
        status = data.get('status', 'present')
        notes = data.get('notes')
        
        success, message = attendance_service.mark_manual_attendance(
            student_id, attendance_date, status, user_id, notes
        )
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
    
    except Exception as e:
        logging.error(f"Mark manual attendance error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/attendance/alerts', methods=['GET'])
@jwt_required()
def get_attendance_alerts():
    """Get irregular attendance alerts"""
    try:
        days_threshold = int(request.args.get('days', 3))
        
        success, alerts = attendance_service.get_irregular_attendance_alerts(days_threshold)
        
        if success:
            return jsonify({'alerts': alerts}), 200
        else:
            return jsonify({'error': alerts}), 400
    
    except Exception as e:
        logging.error(f"Get attendance alerts error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200


@app.route('/api/admin/teachers', methods=['POST'])
@jwt_required()
def create_teacher():
    """Admin endpoint to create a teacher and assign them to a specific class"""
    try:
        user_id = get_jwt_identity()
        admin = User.query.get(user_id)
        if not admin or admin.role != 'admin':
            return jsonify({'error': 'Administrator privileges required'}), 403
        data = request.get_json() or {}
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        class_id = data.get('class_id')  # optional: assign teacher to this class

        # basic validation
        if not username or not email or not password or not full_name:
            return jsonify({'error': 'username, email, password and full_name are required'}), 400

        if User.query.filter((User.username == username) | (User.email == email)).first():
            return jsonify({'error': 'User with this username or email already exists'}), 400

        teacher = User(
            username=username,
            email=email,
            role='teacher',
            full_name=full_name,
            is_active=True
        )
        teacher.set_password(password)

        db.session.add(teacher)
        db.session.flush()  # ensure teacher.id is available

        # Assign to class if provided
        if class_id is not None:
            cls = Class.query.get(class_id)
            if not cls:
                db.session.rollback()
                return jsonify({'error': 'Class not found'}), 400
            if cls.teacher_id:
                db.session.rollback()
                return jsonify({'error': 'Class already has a teacher assigned'}), 400
            cls.teacher_id = teacher.id
            db.session.add(cls)

        db.session.commit()

        # Audit log
        try:
            audit = AuditLog(
                user_id=admin.id,
                action='create_teacher',
                table_name='users',
                record_id=teacher.id,
                old_values=None,
                new_values=json.dumps(teacher.to_dict()),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(audit)
            db.session.commit()
        except Exception:
            db.session.rollback()

        return jsonify({'message': 'Teacher created', 'teacher': teacher.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"Create teacher error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/classes', methods=['GET'])
def list_classes():
    """Return list of classes with assigned teacher info"""
    try:
        classes = Class.query.filter_by(is_active=True).all()
        classes_data = [c.to_dict() for c in classes]
        return jsonify({'classes': classes_data}), 200
    except Exception as e:
        logging.error(f"List classes error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/admin/teachers', methods=['GET'])
@jwt_required()
def list_teachers():
    """Admin-only: list all teacher users"""
    try:
        user_id = get_jwt_identity()
        admin = User.query.get(user_id)
        if not admin or admin.role != 'admin':
            return jsonify({'error': 'Administrator privileges required'}), 403

        teachers = User.query.filter_by(role='teacher').all()
        teachers_data = [t.to_dict() for t in teachers]
        return jsonify({'teachers': teachers_data}), 200
    except Exception as e:
        logging.error(f"List teachers error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/admin/teachers/<int:teacher_id>', methods=['PUT'])
@jwt_required()
def update_teacher(teacher_id):
    """Admin-only: update teacher details and optionally assign/unassign a class"""
    try:
        user_id = get_jwt_identity()
        admin = User.query.get(user_id)
        if not admin or admin.role != 'admin':
            return jsonify({'error': 'Administrator privileges required'}), 403

        teacher = User.query.get(teacher_id)
        if not teacher or teacher.role != 'teacher':
            return jsonify({'error': 'Teacher not found'}), 404

        data = request.get_json() or {}
        # capture old values for audit
        old_values = teacher.to_dict()

        email = data.get('email')
        full_name = data.get('full_name')
        password = data.get('password')
        is_active = data.get('is_active')
        class_id = data.get('class_id') if 'class_id' in data else None

        # Validate email uniqueness
        if email and User.query.filter(User.email == email, User.id != teacher_id).first():
            return jsonify({'error': 'Email already in use'}), 400

        if email:
            teacher.email = email
        if full_name:
            teacher.full_name = full_name
        if isinstance(is_active, bool):
            teacher.is_active = is_active
        if password:
            teacher.set_password(password)

        # Handle class assignment/unassignment
        if class_id is not None:
            if class_id == '':
                # Unassign any class currently assigned to this teacher
                classes = Class.query.filter_by(teacher_id=teacher.id).all()
                for c in classes:
                    c.teacher_id = None
                    db.session.add(c)
            else:
                cls = Class.query.get(class_id)
                if not cls:
                    return jsonify({'error': 'Class not found'}), 400
                # If class already has another teacher, prevent assignment
                if cls.teacher_id and cls.teacher_id != teacher.id:
                    return jsonify({'error': 'Class already has a different teacher assigned'}), 400
                cls.teacher_id = teacher.id
                db.session.add(cls)

        db.session.add(teacher)
        db.session.commit()

        # Audit log for update
        try:
            audit = AuditLog(
                user_id=admin.id,
                action='update_teacher',
                table_name='users',
                record_id=teacher.id,
                old_values=json.dumps(old_values),
                new_values=json.dumps(teacher.to_dict()),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(audit)
            db.session.commit()
        except Exception:
            db.session.rollback()

        return jsonify({'message': 'Teacher updated', 'teacher': teacher.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Update teacher error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/admin/teachers/<int:teacher_id>', methods=['DELETE'])
@jwt_required()
def delete_teacher(teacher_id):
    """Admin-only: delete a teacher user and unassign from classes"""
    try:
        user_id = get_jwt_identity()
        admin = User.query.get(user_id)
        if not admin or admin.role != 'admin':
            return jsonify({'error': 'Administrator privileges required'}), 403

        teacher = User.query.get(teacher_id)
        if not teacher or teacher.role != 'teacher':
            return jsonify({'error': 'Teacher not found'}), 404

        # Unassign classes referencing this teacher
        classes = Class.query.filter_by(teacher_id=teacher.id).all()
        for c in classes:
            c.teacher_id = None
            db.session.add(c)

        # capture old values for audit before deletion
        old_values = teacher.to_dict()
        db.session.delete(teacher)
        db.session.commit()

        # Audit log for delete
        try:
            audit = AuditLog(
                user_id=admin.id,
                action='delete_teacher',
                table_name='users',
                record_id=teacher_id,
                old_values=json.dumps(old_values),
                new_values=None,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(audit)
            db.session.commit()
        except Exception:
            db.session.rollback()

        return jsonify({'message': 'Teacher deleted'}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Delete teacher error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500