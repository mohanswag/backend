import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from api.models import UserProfile

profile = UserProfile.objects.first()

c = Client()
workout_data = {
    "workout_type": "Simulated Full Body",
    "duration_minutes": 45,
    "calories_burned": 320
}
response = c.post(f'/api/history/{profile.username}/', data=json.dumps(workout_data), content_type='application/json')
print(f"Status Code: {response.status_code}")
if response.status_code == 500:
    import builtins
    print(response.content.decode('utf-8')[:2000]) # just show start of error page
