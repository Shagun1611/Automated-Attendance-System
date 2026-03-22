import face_recognition
import cv2
import numpy as np
import os
from PIL import Image
import json
from app.models import Student
from app import db
import logging

class FaceRecognitionService:
    """Service for handling face recognition operations"""
    
    def __init__(self, tolerance=0.6):
        self.tolerance = tolerance
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_student_ids = []
        self.load_known_faces()
    
    def load_known_faces(self):
        """Load all registered student faces from database"""
        try:
            students = Student.query.filter_by(is_active=True).all()
            self.known_face_encodings = []
            self.known_face_names = []
            self.known_student_ids = []
            
            for student in students:
                encodings = student.get_face_encodings()
                for encoding in encodings:
                    self.known_face_encodings.append(np.array(encoding))
                    self.known_face_names.append(student.full_name)
                    self.known_student_ids.append(student.id)
            
            logging.info(f"Loaded {len(self.known_face_encodings)} face encodings for {len(students)} students")
        except Exception as e:
            logging.error(f"Error loading known faces: {str(e)}")
    
    def register_student_faces(self, student_id, image_paths):
        """Register face encodings for a student"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return False, "Student not found"
            
            encodings = []
            for image_path in image_paths:
                # Load image
                image = face_recognition.load_image_file(image_path)
                
                # Find face encodings
                face_encodings = face_recognition.face_encodings(image)
                
                if len(face_encodings) == 0:
                    logging.warning(f"No face found in image: {image_path}")
                    continue
                
                if len(face_encodings) > 1:
                    logging.warning(f"Multiple faces found in image: {image_path}")
                    # Use the first face encoding
                
                encodings.append(face_encodings[0].tolist())
            
            if not encodings:
                return False, "No valid faces found in provided images"
            
            # Store encodings in database
            student.set_face_encodings(encodings)
            db.session.commit()
            
            # Reload known faces
            self.load_known_faces()
            
            return True, f"Registered {len(encodings)} face encodings for {student.full_name}"
        
        except Exception as e:
            logging.error(f"Error registering student faces: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def recognize_faces(self, image_data):
        """Recognize faces in the given image"""
        try:
            # Convert image data to numpy array
            if isinstance(image_data, str):
                # If image_data is a file path
                image = face_recognition.load_image_file(image_data)
            else:
                # If image_data is raw image data
                image = np.array(image_data)
            
            # Find all face locations and encodings in the image
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            recognized_faces = []
            
            for face_encoding, face_location in zip(face_encodings, face_locations):
                # Compare with known faces
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=self.tolerance)
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    
                    if matches[best_match_index]:
                        student_id = self.known_student_ids[best_match_index]
                        student_name = self.known_face_names[best_match_index]
                        confidence = 1 - face_distances[best_match_index]
                        
                        recognized_faces.append({
                            'student_id': student_id,
                            'student_name': student_name,
                            'confidence': float(confidence),
                            'face_location': face_location
                        })
            
            return True, recognized_faces
        
        except Exception as e:
            logging.error(f"Error recognizing faces: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def extract_face_from_image(self, image_path, output_path=None):
        """Extract and save face from image"""
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            
            if len(face_locations) == 0:
                return False, "No face found in image"
            
            if len(face_locations) > 1:
                logging.warning("Multiple faces found, using the first one")
            
            # Get the first face
            top, right, bottom, left = face_locations[0]
            
            # Extract face region with some padding
            padding = 20
            face_image = image[max(0, top-padding):bottom+padding, 
                             max(0, left-padding):right+padding]
            
            if output_path:
                # Convert RGB to BGR for OpenCV
                face_image_bgr = cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR)
                cv2.imwrite(output_path, face_image_bgr)
            
            return True, face_image
        
        except Exception as e:
            logging.error(f"Error extracting face: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def validate_image_quality(self, image_path):
        """Validate if image is suitable for face recognition"""
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)
            
            # Check image dimensions
            height, width = image.shape[:2]
            if height < 200 or width < 200:
                return False, "Image resolution too low (minimum 200x200)"
            
            # Find faces
            face_locations = face_recognition.face_locations(image)
            
            if len(face_locations) == 0:
                return False, "No face detected in image"
            
            if len(face_locations) > 1:
                return False, "Multiple faces detected. Please use image with single face"
            
            # Check face size
            top, right, bottom, left = face_locations[0]
            face_height = bottom - top
            face_width = right - left
            
            if face_height < 100 or face_width < 100:
                return False, "Face too small in image"
            
            # Try to extract face encoding
            face_encodings = face_recognition.face_encodings(image, face_locations)
            if len(face_encodings) == 0:
                return False, "Could not extract face features"
            
            return True, "Image quality is good for face recognition"
        
        except Exception as e:
            logging.error(f"Error validating image: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def update_student_encoding(self, student_id, new_image_path):
        """Update face encoding for existing student"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return False, "Student not found"
            
            # Validate new image
            is_valid, message = self.validate_image_quality(new_image_path)
            if not is_valid:
                return False, message
            
            # Get existing encodings
            existing_encodings = student.get_face_encodings()
            
            # Add new encoding
            image = face_recognition.load_image_file(new_image_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if face_encodings:
                existing_encodings.append(face_encodings[0].tolist())
                
                # Limit to maximum 5 encodings per student
                if len(existing_encodings) > 5:
                    existing_encodings = existing_encodings[-5:]
                
                student.set_face_encodings(existing_encodings)
                db.session.commit()
                
                # Reload known faces
                self.load_known_faces()
                
                return True, f"Updated face encoding for {student.full_name}"
            else:
                return False, "Could not extract face encoding from image"
        
        except Exception as e:
            logging.error(f"Error updating student encoding: {str(e)}")
            return False, f"Error: {str(e)}"