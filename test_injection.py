import requests
import json

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "your_api_key_here"  # Replace with your actual API key

def test_url_injection():
    print("Testing URL injection attack...")
    # Test with a MongoDB operator in URL
    response = requests.get(f"{BASE_URL}/scores?query={{'$where':'true'}}")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    print("-" * 50)

def test_json_injection():
    print("Testing JSON injection attack...")
    # Test with MongoDB operator in JSON payload
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "player_name": "player$where",  # Invalid character
        "score": 100
    }
    response = requests.post(f"{BASE_URL}/scores", headers=headers, json=payload)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    print("-" * 50)

if __name__ == "__main__":
    test_url_injection()
    test_json_injection()