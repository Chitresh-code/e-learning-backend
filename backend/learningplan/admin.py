from django.contrib import admin
from .models import (
    LearningPlan,
    LearningPlanWeek,
    LearningPlanResource,
)

# Register your models here.
@admin.register(LearningPlan)
class LearningPlanAdmin(admin.ModelAdmin):
    list_display = ("student", "plan_duration_weeks", "created_at")
    search_fields = ("student__email",)
    ordering = ("-created_at",)


@admin.register(LearningPlanWeek)
class LearningPlanWeekAdmin(admin.ModelAdmin):
    list_display = ("plan", "week")
    search_fields = ("plan__student__email",)


@admin.register(LearningPlanResource)
class LearningPlanResourceAdmin(admin.ModelAdmin):
    list_display = ("week", "fallback_name", "resource")
    search_fields = ("fallback_name", "resource__topic_name", "week__plan__student__email")