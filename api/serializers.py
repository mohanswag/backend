from rest_framework import serializers
from .models import AnalysisRequest, UserProfile, AppNotification, WorkoutSession, StreakRecord, ExerciseVideo

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'username', 'email', 'password', 'name', 'profile_image_base64',
            'streak', 'calories_burned', 'weekly_progress',
            'age', 'height', 'weight', 'total_workouts', 'total_calories', 'active_days',
            'push_notifications', 'workout_reminders', 'achievement_alerts',
            'dark_mode', 'language'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        from django.contrib.auth.hashers import make_password
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class WorkoutSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutSession
        fields = ['id', 'user_profile', 'date', 'workout_type', 'duration_minutes', 'calories_burned']
        read_only_fields = ['id', 'date', 'user_profile']

class StreakRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreakRecord
        fields = ['id', 'user_profile', 'date', 'logged_in']
        read_only_fields = ['id', 'date']

class AppNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppNotification
        fields = ['id', 'title', 'message', 'notification_type', 'scheduled_time', 'created_at', 'is_read']

class AnalysisRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisRequest
        fields = ['id', 'user_input', 'ai_result', 'created_at']

class ExerciseVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseVideo
        fields = ['id', 'name', 'video_file', 'created_at']
