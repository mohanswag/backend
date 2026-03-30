import requests
import datetime
from django.utils import timezone
from .models import UserProfile, AppNotification, WorkoutSession, StreakRecord

class NotificationEngine:
    FASTAPI_URL = "http://localhost:8000/generate_notification/"

    @classmethod
    def generate_periodic_notifications(cls):
        """Run this via a management command or task scheduler"""
        now = timezone.now()
        hour = now.hour
        
        users = UserProfile.objects.filter(push_notifications=True)
        
        for user in users:
            # Determine notification type based on time
            # 7-9 AM: MORNING
            # 12-2 PM: DIET
            # 5-7 PM: EVENING
            # 9-11 PM: NIGHT
            
            n_type = None
            if 7 <= hour <= 9:
                n_type = 'MORNING'
            elif 12 <= hour <= 14:
                n_type = 'DIET'
            elif 17 <= hour <= 19:
                n_type = 'EVENING'
            elif 21 <= hour <= 23:
                n_type = 'NIGHT'
            
            if n_type:
                # Check if we already sent this type today
                today_min = now.replace(hour=0, minute=0, second=0, microsecond=0)
                exists = AppNotification.objects.filter(
                    user_profile=user, 
                    notification_type=n_type, 
                    created_at__gte=today_min
                ).exists()
                
                if not exists:
                    cls.create_ai_notification(user, n_type)

    @classmethod
    def create_event_notification(cls, user, n_type, event_title=None):
        """Triggered by specific app events like saving a workout or streak update"""
        return cls.create_ai_notification(user, n_type, event_title)

    @classmethod
    def create_ai_notification(cls, user, n_type, override_title=None):
        payload = {
            "user_name": user.name or user.username,
            "streak": user.streak,
            "calories_today": user.calories_burned,
            "total_workouts": user.total_workouts,
            "notification_type": n_type,
            "language": user.language
        }
        
        try:
            response = requests.post(cls.FASTAPI_URL, json=payload, timeout=5)
            if response.status_code == 200:
                data = response.json()
                title = override_title or data.get("title", "FlexAI Update")
                message = data.get("message", "Keep going!")
                
                AppNotification.objects.create(
                    user_profile=user,
                    title=title,
                    message=message,
                    notification_type=n_type
                )
                return
        except Exception as e:
            print(f"Error calling FastAPI for notification: {e}")

        # Fallback simple notification (if FastAPI fails or returns non-200)
        AppNotification.objects.create(
            user_profile=user,
            title=override_title or "FlexAI Goal Reminder",
            message="Your fitness journey continues! Stay consistent today.",
            notification_type=n_type
        )

    @classmethod
    def check_inactivity(cls):
        """Check for users who haven't logged in today"""
        now = timezone.now()
        today = now.date()
        
        users = UserProfile.objects.filter(push_notifications=True)
        for user in users:
            last_record = StreakRecord.objects.filter(user_profile=user).order_by('-date').first()
            if not last_record or last_record.date < today:
                # Check if we already reminded them about inactivity today
                today_min = now.replace(hour=0, minute=0, second=0, microsecond=0)
                if not AppNotification.objects.filter(user_profile=user, title__icontains="Inactivity", created_at__gte=today_min).exists():
                    cls.create_event_notification(user, 'EVENT', "Inactivity Alert")
