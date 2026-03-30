from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalysisRequestViewSet, UserProfileViewSet, AppNotificationViewSet, WorkoutSessionViewSet, StreakRecordViewSet, ExerciseVideoViewSet, ChatBotView, trigger_notifications

router = DefaultRouter()
router.register(r'analyze', AnalysisRequestViewSet, basename='analyze')
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'videos', ExerciseVideoViewSet, basename='video')

urlpatterns = [
    path('', include(router.urls)),
    path('notifications/trigger/', trigger_notifications, name='trigger-notifications'),
    path('notifications/<str:username>/', AppNotificationViewSet.as_view({'get': 'list'}), name='notification-list'),
    path('history/<str:username>/', WorkoutSessionViewSet.as_view({'get': 'list', 'post': 'create'}), name='history-list'),
    path('streaks/<str:username>/', StreakRecordViewSet.as_view({'get': 'list'}), name='streak-list'),
    path('chat/', ChatBotView.as_view(), name='ai-chat'),
]
