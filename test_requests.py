import requests
import json

base_url = "http://127.0.0.1:8000/api"
username = "shotvi555705"

print("1. Fetching live stats...")
r1 = requests.get(f"{base_url}/profiles/{username}/")
if r1.status_code == 200:
    print(f"Calories before: {r1.json().get('calories_burned')}")
else:
    print(f"Error {r1.status_code}: {r1.text}")

print("2. Simulating workout...")
workout_data = {
    "workout_type": "Simulated Full Body",
    "duration_minutes": 45,
    "calories_burned": 320
}
r2 = requests.post(f"{base_url}/history/{username}/", json=workout_data)
if r2.status_code in [200, 201]:
    print("Workout created successfully!")
else:
    print(f"Error {r2.status_code}: {r2.text}")

print("3. Fetching live stats again...")
r3 = requests.get(f"{base_url}/profiles/{username}/")
if r3.status_code == 200:
    print(f"Calories after: {r3.json().get('calories_burned')}")
else:
    print(f"Error {r3.status_code}: {r3.text}")
