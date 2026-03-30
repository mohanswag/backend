from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from .models import AnalysisRequest, UserProfile, AppNotification, WorkoutSession, StreakRecord, ExerciseVideo, PasswordResetOTP
from .serializers import AnalysisRequestSerializer, UserProfileSerializer, AppNotificationSerializer, WorkoutSessionSerializer, StreakRecordSerializer, ExerciseVideoSerializer
from django.conf import settings
import requests
import os
import random
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

from .notification_engine import NotificationEngine
from django.http import JsonResponse
from rest_framework.decorators import api_view

@api_view(['POST'])
def trigger_notifications(request):
    """Admin or manual trigger for periodic notifications"""
    NotificationEngine.generate_periodic_notifications()
    NotificationEngine.check_inactivity()
    return JsonResponse({"status": "Notifications triggered successfully"})

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'username'

    def retrieve(self, request, *args, **kwargs):
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Sum
        
        instance = self.get_object()
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)
        
        # If the user opens the app (login), write a StreakRecord for today
        StreakRecord.objects.get_or_create(
            user_profile=instance, date=today,
            defaults={'logged_in': True}
        )
        
        # Calculate exactly how many unbroken days we've logged in backwards
        current_streak = 0
        loop_date = today
        while StreakRecord.objects.filter(user_profile=instance, date=loop_date, logged_in=True).exists():
            current_streak += 1
            loop_date -= timedelta(days=1)
            
        if instance.streak != current_streak:
            instance.streak = current_streak
            instance.save()
            
        # Calculate exactly how many calories burned TODAY
        from datetime import datetime, time
        start_of_day = timezone.make_aware(datetime.combine(today, time.min))
        end_of_day = timezone.make_aware(datetime.combine(today, time.max))
        today_workouts = WorkoutSession.objects.filter(user_profile=instance, date__gte=start_of_day, date__lte=end_of_day)
        today_calories = today_workouts.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0
        
        if instance.calories_burned != today_calories:
            instance.calories_burned = today_calories
            instance.save()
                
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({'error': 'Please provide email and password'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            profile = UserProfile.objects.get(email=email)
            if check_password(password, profile.password):
                return Response({'success': True, 'username': profile.username})
            else:
                return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def request_reset(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            profile = UserProfile.objects.get(email=email)
            # Generate 6-digit OTP
            otp = str(random.randint(100000, 999999))
            
            # Save OTP to database
            PasswordResetOTP.objects.create(user_profile=profile, otp=otp)
            
            # Send email
            send_mail(
                'Your Password Reset OTP',
                f'Your OTP for resetting your password is: {otp}. It is valid for 15 minutes.',
                'noreply@flexai.com',
                [email],
                fail_silently=False,
            )
            return Response({'success': True, 'message': 'OTP sent successfully'})
        except UserProfile.DoesNotExist:
            return Response({'error': 'User with this email not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def verify_reset(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        
        if not all([email, otp, new_password]):
            return Response({'error': 'Email, OTP, and new password are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            profile = UserProfile.objects.get(email=email)
            
            # Find the latest matching OTP for this user
            valid_time = timezone.now() - timedelta(minutes=15)
            reset_otp = PasswordResetOTP.objects.filter(
                user_profile=profile, 
                otp=otp,
                created_at__gte=valid_time
            ).order_by('-created_at').first()
            
            if reset_otp:
                # Set new password
                from django.contrib.auth.hashers import make_password
                profile.password = make_password(new_password)
                profile.save()
                
                # Delete the used OTP (and any older ones)
                PasswordResetOTP.objects.filter(user_profile=profile).delete()
                
                return Response({'success': True, 'message': 'Password reset successfully'})
            else:
                return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
                
        except UserProfile.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class AppNotificationViewSet(viewsets.ModelViewSet):
    serializer_class = AppNotificationSerializer
    
    def get_queryset(self):
        username = self.kwargs.get('username')
        if username:
            return AppNotification.objects.filter(user_profile__username=username).order_by('-created_at')
        return AppNotification.objects.none()

class WorkoutSessionViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutSessionSerializer
    
    def get_queryset(self):
        username = self.kwargs.get('username')
        if username:
            return WorkoutSession.objects.filter(user_profile__username=username).order_by('-date')
        return WorkoutSession.objects.none()

    def perform_create(self, serializer):
        from django.utils import timezone
        from datetime import timedelta
        username = self.kwargs.get('username')
        profile = UserProfile.objects.get(username=username)

        # 1. Save Workout
        session = serializer.save(user_profile=profile)

        # 2. Update Basic Stats (Increment calories uniformly)
        profile.total_workouts += 1
        profile.total_calories += session.calories_burned
        profile.calories_burned += session.calories_burned

        # 3. Assess Weekly Progress Ratio based on workouts THIS WEEK
        today = timezone.localdate()
        start_of_week = today - timedelta(days=today.weekday())
        
        sessions_this_week = WorkoutSession.objects.filter(
            user_profile=profile,
            date__gte=start_of_week
        )
        worked_dates = set([timezone.localtime(s.date).date() for s in sessions_this_week])
        active_days = len(worked_dates)
        
        profile.active_days = WorkoutSession.objects.filter(user_profile=profile).values('date__date').distinct().count()
        profile.weekly_progress = int(round((active_days / 7.0) * 100))
        profile.save()

class StreakRecordViewSet(viewsets.ModelViewSet):
    serializer_class = StreakRecordSerializer
    
    def get_queryset(self):
        username = self.kwargs.get('username')
        if username:
            return StreakRecord.objects.filter(user_profile__username=username).order_by('-date')
        return StreakRecord.objects.none()

class AnalysisRequestViewSet(viewsets.ModelViewSet):
    queryset = AnalysisRequest.objects.all()
    serializer_class = AnalysisRequestSerializer

    def create(self, request, *args, **kwargs):
        # Create the initial request
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        analysis_request = serializer.save()

        # Send prompt securely to the local HuggingFace ML instance
        user_input = analysis_request.user_input
        fastapi_url = "http://127.0.0.1:8001/chat/"
        
        try:
            payload = {
                "message": user_input,
                "system_prompt": "You are a highly motivating personal trainer. Keep it exactly one sentence and engaging."
            }
            ml_response = requests.post(fastapi_url, json=payload, timeout=120)
            if ml_response.status_code == 200:
                ai_text = ml_response.json().get('response', 'Error reading response.')
                analysis_request.ai_result = ai_text
            else:
                analysis_request.ai_result = "AI Model Error: " + ml_response.text
        except requests.exceptions.ConnectionError:
            analysis_request.ai_result = "AI Error: Model server is offline. Please deploy port 8001."
        except Exception as e:
            analysis_request.ai_result = f"AI Error: {str(e)}"
        
        # Update and save the result
        analysis_request.save()

        # Return the updated object
        updated_serializer = self.get_serializer(analysis_request)
        return Response(updated_serializer.data, status=status.HTTP_201_CREATED)

class ExerciseVideoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExerciseVideo.objects.all()
    serializer_class = ExerciseVideoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name=name)
        return queryset

class ChatBotView(APIView):
    def post(self, request, *args, **kwargs):
        user_message = request.data.get('message')
        res_language = request.data.get('language', 'English')
        if not user_message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            prompt_path = os.path.join(settings.BASE_DIR, 'api', 'prompt.txt')
            with open(prompt_path, 'r', encoding='utf-8', errors='ignore') as file:
                system_prompt = file.read()
            
            system_prompt += f"\n\nIMPORTANT: You MUST respond completely in the {res_language} language."
            
            fastapi_url = "http://127.0.0.1:8001/chat/"
            
            payload = {
                "message": user_message,
                "system_prompt": system_prompt
            }
            
            ml_response = requests.post(fastapi_url, json=payload, timeout=120)
            
            if ml_response.status_code == 200:
                ai_text = ml_response.json().get('response', 'Error reading response from FastAPI.')
                
                # Keep original utf-8 AI text natively for App display
                safe_ai_text = ai_text
                
                return Response({'response': safe_ai_text}, status=status.HTTP_200_OK)
            else:
                return Response({'error': f"FastAPI Server Error: {ml_response.text}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except requests.exceptions.ConnectionError:
            return Response({'error': "FastAPI ML Server is offline. Please start it on port 8001."}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as e:
            return Response({'error': f"AI Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
