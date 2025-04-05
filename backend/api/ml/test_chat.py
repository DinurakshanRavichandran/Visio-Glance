import requests
import json

def test_chat_endpoint():
    # Update with your actual backend URL
    BASE_URL = "http://localhost:5000/api/ml/chat"
    
    # Test payloads
    test_cases = [
        {"message": "What is diabetes?"},  # Valid request
        {},  # Missing message
        {"message": "Explain retinal fundus imaging"}  # Another valid request
    ]

    for idx, payload in enumerate(test_cases, 1):
        print(f"\nTest Case {idx}: {payload}")
        
        try:
            response = requests.post(
                BASE_URL,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )
            
            print(f"Status Code: {response.status_code}")
            print("Response:")
            print(json.dumps(response.json(), indent=2))
            
        except requests.exceptions.RequestException as e:
            print(f"Connection Error: {str(e)}")
        except Exception as e:
            print(f"Unexpected Error: {str(e)}")

if __name__ == "__main__":
    test_chat_endpoint()