from rest_framework import serializers
from django.contrib.auth import authenticate
from student.models import (
    Student, StudentInfo, Subject, StudentSubject,
    Quiz, Question, LearningGoal, Resource, StudentResourceLog
)

# ---------------------------
# Authentication Serializers
# ---------------------------
class StudentLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"}, trim_whitespace=False)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(request=self.context.get("request"), email=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid email or password", code="authorization")
        else:
            raise serializers.ValidationError("Both email and password are required")

        data["user"] = user
        return data

class StudentRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = Student
        fields = ("email", "password")

    def create(self, validated_data):
        return Student.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"]
        )

# ---------------------------
# Student Info & Subject Data
# ---------------------------
class StudentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentInfo
        exclude = ["id", "joined_on"]
        read_only_fields = ["student"]

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "name", "description"]

class StudentSubjectSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(write_only=True)
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = StudentSubject
        exclude = ["id"]
        read_only_fields = ["student", "subject"]

    def create(self, validated_data):
        subject_name = validated_data.pop("subject_name")
        subject, _ = Subject.objects.get_or_create(name=subject_name)
        return StudentSubject.objects.create(
            student=self.context["request"].user,
            subject=subject,
            **validated_data
        )

# ---------------------------
# Quiz & Question
# ---------------------------
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        exclude = ["id"]
        read_only_fields = ["quiz"]

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)
    subject_name = serializers.CharField(write_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id", "student", "subject", "subject_name", "total_marks",
            "score", "ai_feedback", "status", "created_at", "questions"
        ]
        read_only_fields = ["id", "student", "created_at", "subject", "questions"]

    def create(self, validated_data):
        subject_name = validated_data.pop("subject_name")
        questions_data = validated_data.pop("questions", [])
        student = self.context["request"].user

        subject, _ = Subject.objects.get_or_create(name=subject_name)
        quiz = Quiz.objects.create(student=student, subject=subject, **validated_data)

        for question in questions_data:
            Question.objects.create(quiz=quiz, **question)

        return quiz

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["subject"] = {
            "id": instance.subject.id,
            "name": instance.subject.name
        }
        return data

# ---------------------------
# Goals and Resources
# ---------------------------
class LearningGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningGoal
        exclude = ["id", "created_at"]
        read_only_fields = ["student"]

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = "__all__"

class StudentResourceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentResourceLog
        exclude = ["id"]
        read_only_fields = ["student", "accessed_at"]
        
        
# ---------------------------
# Full Student Data Serializer
# ---------------------------
class FullStudentDataSerializer(serializers.Serializer):
    email = serializers.EmailField()
    info = StudentInfoSerializer()
    subjects = StudentSubjectSerializer(many=True)
    quizzes = serializers.SerializerMethodField()
    goals = LearningGoalSerializer(many=True)
    resource_logs = StudentResourceLogSerializer(many=True)

    def get_info(self, obj):
        return StudentInfoSerializer(self.context["info"]).data

    def get_subjects(self, obj):
        return StudentSubjectSerializer(self.context["subjects"], many=True).data

    def get_goals(self, obj):
        return LearningGoalSerializer(self.context["goals"], many=True).data

    def get_resource_logs(self, obj):
        return StudentResourceLogSerializer(self.context["resource_logs"], many=True).data

    def get_quizzes(self, obj):
        quizzes = Quiz.objects.filter(student=obj).values(
            "id", "subject__id", "subject__name", "total_marks", "score", "ai_feedback", "status", "created_at"
        )
        return list(quizzes)

    def to_representation(self, instance):
        return {
            "email": instance.email,
            "info": self.get_info(instance),
            "subjects": self.get_subjects(instance),
            "quizzes": self.get_quizzes(instance),
            "goals": self.get_goals(instance),
            "resource_logs": self.get_resource_logs(instance),
        }