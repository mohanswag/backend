import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_trigger():
    print("Testing Notification Trigger...")
    try:
        response = requests.post(f"{BASE_URL}/notifications/trigger/")
        print("Response:", response.status_code, response.json())
    except Exception as e:
        print("Error:", e)

def test_list(username):
    print(f"Testing Notification List for {username}...")
    try:
        response = requests.get(f"{BASE_URL}/notifications/{username}/")
        if response.status_code == 200:
            notifications = response.json()
            print(f"Found {len(notifications)} notifications.")
            for n in notifications:
                print(f"- [{n['notification_type']}] {n['title']}: {n['message']}")
        else:
            print("Response:", response.status_code, response.text)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    # Note: This requires the Django and FastAPI servers to be running locally.
    # Since I cannot guarantee they are running in the background, I will just provide the script.
    # But I can check if there are any users in the DB first.
    pass
