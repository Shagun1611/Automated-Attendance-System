import requests
import base64

def test_base64_recognition():
    """Test the base64 image processing endpoint"""
    url = "http://localhost:5000/api/attendance/recognize"
    
    # Create a simple test base64 image (1x1 red pixel)
    # This is just to test the base64 processing, not actual face recognition
    test_image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    print(f"Testing base64 endpoint: {url}")
    
    try:
        # Test base64 image processing
        response = requests.post(url, data={'image_data': test_image_data})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        # The response should be a 400 error saying "No faces detected in the image"
        # which means the base64 processing worked, but no faces were found (expected)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing Base64 Face Recognition Processing")
    print("=" * 50)
    test_base64_recognition()