import requests
import os

# Configuration
API_URL = "http://localhost:5000/analyze"
TEST_IMAGE_PATH = os.path.normpath(r"C:\Users\Dinurakshan\Visio-Glance\backend\api\ml\cnv.jpeg")

def test_analysis():
    # Verify file exists first
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"Error: Test image not found at {TEST_IMAGE_PATH}")
        print("Current directory:", os.getcwd())
        return

    # Prepare and send request
    try:
        with open(TEST_IMAGE_PATH, "rb") as image_file:
            files = {"image": ("test_image.jpeg", image_file, "image/jpeg")}
            response = requests.post(API_URL, files=files)
            
            # Check response
            assert response.status_code == 200
            result = response.json()
            
            print("\nAnalysis Result:")
            print(f"Prediction: {result['classification']['prediction']}")
            print(f"Confidence: {result['classification']['confidence']:.4f}")
            print(f"LIME Explanation: {result['explanations']['lime']}")
            print(f"SHAP Explanation: {result['explanations']['shap']}")
            
    except Exception as e:
        print(f"Error during test: {str(e)}")

if __name__ == "__main__":
    test_analysis()