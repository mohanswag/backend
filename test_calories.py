import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import UserProfile, WorkoutSession
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum

username = "shotvi555"
try:
    profile = UserProfile.objects.get(username__icontains="shotvi")
    print(f"Profile: {profile.username}")
    
    today = timezone.localdate()
    today_workouts = WorkoutSession.objects.filter(user_profile=profile, date__date=today)
    
    print(f"Today's date: {today}")
    for w in WorkoutSession.objects.filter(user_profile=profile):
        print(f"Workout: {w.date} (Type: {type(w.date)}) -> {w.calories_burned}")
        
    print(f"Workouts today count: {today_workouts.count()}")
    today_calories = today_workouts.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0
    print(f"Calculated calories for today: {today_calories}")
    
except Exception as e:
    print(f"Error: {e}")
