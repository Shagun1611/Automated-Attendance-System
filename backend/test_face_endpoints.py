import requests
import os

def test_face_recognition_endpoint():
    """Test the face recognition endpoint to debug the issue"""
    url = "http://localhost:5000/api/attendance/recognize"
    
    # Create a simple test image (this won't work for actual recognition but will test the endpoint)
    print(f"Testing endpoint: {url}")
    
    # Test 1: No file sent
    print("\n--- Test 1: No file in request ---")
    try:
        response = requests.post(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Empty files dict
    print("\n--- Test 2: Empty files dict ---")
    try:
        response = requests.post(url, files={})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Photo field but no actual file
    print("\n--- Test 3: Photo field with empty content ---")
    try:
        response = requests.post(url, files={'photo': ('test.jpg', '', 'image/jpeg')})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_upload_photo_endpoint():
    """Test the upload photo endpoint"""
    student_id = 1  # Assuming student with ID 1 exists
    url = f"http://localhost:5000/api/students/{student_id}/upload-photo"
    
    print(f"\n\nTesting endpoint: {url}")
    
    # Test 1: No file sent
    print("\n--- Test 1: No file in request ---")
    try:
        response = requests.post(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing Face Recognition Endpoints")
    print("=" * 50)
    
    test_face_recognition_endpoint()
    test_upload_photo_endpoint()