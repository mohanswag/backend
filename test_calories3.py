import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import UserProfile, WorkoutSession
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Sum

username = "shotvi555"
try:
    profile = UserProfile.objects.get(username__icontains="shotvi")
    print(1)
    session = WorkoutSession.objects.create(
        user_profile=profile,
        workout_type="Simulated",
        duration_minutes=45,
        calories_burned=320
    )
    print(2)
    today = timezone.localdate()
    start_of_week = today - timedelta(days=today.weekday())
    print(3)
    sessions_this_week = WorkoutSession.objects.filter(
        user_profile=profile,
        date__gte=start_of_week
    )
    worked_dates = set([timezone.localtime(s.date).date() for s in sessions_this_week])
    active_days = len(worked_dates)
    print(4)
    c = WorkoutSession.objects.filter(user_profile=profile).values('date__date').distinct().count()
    print(f"5: {c}")
except Exception as e:
    print(f"Error: {e}")
