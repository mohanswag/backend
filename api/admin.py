from django.contrib import admin
from .models import AnalysisRequest, UserProfile, AppNotification, WorkoutSession, StreakRecord, ExerciseVideo

admin.site.register(UserProfile)
admin.site.register(WorkoutSession)
admin.site.register(StreakRecord)
admin.site.register(AppNotification)
admin.site.register(AnalysisRequest)

@admin.register(ExerciseVideo)
class ExerciseVideoAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
