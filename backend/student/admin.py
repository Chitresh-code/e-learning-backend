from django.contrib import admin
from .models import (
    Student, StudentInfo, Subject, StudentSubject,
    Quiz, Question, LearningGoal,
    Resource, StudentResourceLog
)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "is_staff", "date_joined")
    search_fields = ("email",)

@admin.register(StudentInfo)
class StudentInfoAdmin(admin.ModelAdmin):
    list_display = ("student", "full_name", "age", "preferred_learning_style")

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(StudentSubject)
class StudentSubjectAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "preferred_style")

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "subject", "status", "score", "created_at")
    list_filter = ("status",)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("quiz", "question_text", "is_correct")

@admin.register(LearningGoal)
class LearningGoalAdmin(admin.ModelAdmin):
    list_display = ("student", "goal_text", "subject", "achieved")

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("topic_name", "subject", "type")

@admin.register(StudentResourceLog)
class StudentResourceLogAdmin(admin.ModelAdmin):
    list_display = ("student", "resource", "accessed_at")