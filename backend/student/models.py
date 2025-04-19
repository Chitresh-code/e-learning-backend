from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# -----------------------------
# Auth: Student + Manager
# -----------------------------

class StudentManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class Student(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = StudentManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


# -----------------------------
# Student Info
# -----------------------------

class StudentInfo(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="info")
    full_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10)

    LEARNING_STYLE_CHOICES = [
        ("visual", "Visual"),
        ("auditory", "Auditory"),
        ("reading_writing", "Reading/Writing"),
        ("kinesthetic", "Kinesthetic"),
    ]
    preferred_learning_style = models.CharField(max_length=50, choices=LEARNING_STYLE_CHOICES)
    joined_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.student.email})"


# -----------------------------
# Subject
# -----------------------------

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# -----------------------------
# Student <-> Subject personalization
# -----------------------------

class StudentSubject(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="subjects")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="student_links")

    STYLE_CHOICES = [
        ("visual", "Visual"),
        ("auditory", "Auditory"),
        ("reading_writing", "Reading/Writing"),
        ("kinesthetic", "Kinesthetic"),
    ]
    preferred_style = models.CharField(max_length=50, choices=STYLE_CHOICES)

    favorite_topics = models.JSONField(blank=True, null=True)  # {"Topic A": "reason", ...}
    weak_topics = models.JSONField(blank=True, null=True)      # {"Topic B": "reason", ...}
    goal = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("student", "subject")

    def __str__(self):
        return f"{self.student.email} - {self.subject.name}"


# -----------------------------
# Quiz
# -----------------------------

class Quiz(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="quizzes")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_marks = models.PositiveIntegerField()
    score = models.FloatField(null=True, blank=True)
    ai_feedback = models.TextField(blank=True)

    STATUS_CHOICES = [("pending", "Pending"), ("completed", "Completed")]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"Quiz {self.id} - {self.student.email} - {self.subject.name}"


# -----------------------------
# Question
# -----------------------------

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    options = models.JSONField()  # {"A": "...", "B": "...", ...}
    correct_option = models.CharField(max_length=255)
    student_answer = models.CharField(max_length=255, blank=True)
    is_correct = models.BooleanField(null=True)

    def __str__(self):
        return f"Q{self.id} for Quiz {self.quiz.id}"


# -----------------------------
# Learning Goal
# -----------------------------

class LearningGoal(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="goals")
    goal_text = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    achieved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.email} - {self.goal_text}"


# -----------------------------
# Resource
# -----------------------------

class Resource(models.Model):
    RESOURCE_TYPE_CHOICES = [
        ("video", "Video"),
        ("article", "Article"),
        ("leetcode", "LeetCode"),
        ("notes", "Notes"),
    ]

    topic_name = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    url = models.URLField()
    type = models.CharField(max_length=50, choices=RESOURCE_TYPE_CHOICES)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.topic_name} [{self.type}]"


# -----------------------------
# Student ↔ Resource Log
# -----------------------------

class StudentResourceLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    accessed_at = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student.email} -> {self.resource.topic_name}"