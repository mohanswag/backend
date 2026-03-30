import requests
import json

url = "http://127.0.0.1:8000/api/chat/"
payload = {"message": "hello gym coach"}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=payload)
    print("Status:", response.status_code)
    safe_text = response.text.encode('ascii', 'ignore').decode('ascii')
    print("Response:", safe_text)
except Exception as e:
    print("Error:", e)
