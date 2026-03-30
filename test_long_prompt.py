import requests

url = "http://127.0.0.1:8001/chat/"
data = {
    "message": "hello I need a detailed explanation on gym",
    "system_prompt": "You are a professional fitness coach."
}

response = requests.post(url, json=data)
print("Status:", response.status_code)
print("Response:", response.json())
