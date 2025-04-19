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
        fields = "__all__"

class StudentSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSubject
        exclude = ["id"]
        read_only_fields = ["student"]

# ---------------------------
# Quiz & Question
# ---------------------------
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        exclude = ["id"]
        read_only_fields = ["quiz"]

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = "__all__"
        read_only_fields = ["student", "created_at", "questions"]

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