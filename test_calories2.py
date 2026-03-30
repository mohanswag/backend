import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import UserProfile, WorkoutSession
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Sum
from datetime import time

username = "shotvi555"
try:
    profile = UserProfile.objects.get(username__icontains="shotvi")
    print(f"Profile: {profile.username}")
    
    today = timezone.localdate()
    
    # manual range
    start_of_day = timezone.make_aware(datetime.combine(today, time.min))
    end_of_day = timezone.make_aware(datetime.combine(today, time.max))
    
    today_workouts_range = WorkoutSession.objects.filter(user_profile=profile, date__gte=start_of_day, date__lte=end_of_day)

    for w in WorkoutSession.objects.filter(user_profile=profile):
        print(f"Workout: {w.date} (Type: {type(w.date)}) -> {w.calories_burned}")
        
    print(f"Workouts today count range: {today_workouts_range.count()}")
    today_calories_range = today_workouts_range.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0
    print(f"Calculated calories for today: {today_calories_range}")
    
except Exception as e:
    print(f"Error: {e}")
