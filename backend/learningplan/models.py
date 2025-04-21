from django.db import models
from student.models import Student, Resource

class LearningPlan(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    plan_duration_weeks = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Plan ({self.student.email})"


class LearningPlanWeek(models.Model):
    plan = models.ForeignKey(LearningPlan, related_name="weeks", on_delete=models.CASCADE)
    week = models.PositiveIntegerField()
    focus_topics = models.JSONField()
    practice_tasks = models.JSONField()
    ai_message = models.TextField()

    def __str__(self):
        return f"Week {self.week} of Plan ({self.plan.student.email})"


class LearningPlanResource(models.Model):
    week = models.ForeignKey(LearningPlanWeek, related_name="resources", on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.SET_NULL, null=True, blank=True)
    fallback_name = models.CharField(max_length=255)
    fallback_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.fallback_name} for {self.week}"