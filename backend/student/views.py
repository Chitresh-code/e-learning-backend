from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import (
    StudentInfo, StudentSubject, Subject, LearningGoal,
    Quiz, Question, Resource, StudentResourceLog
)
from .serializers import (
    StudentLoginSerializer, StudentRegisterSerializer,
    StudentInfoSerializer, StudentSubjectSerializer,
    SubjectSerializer, QuizSerializer, QuestionSerializer,
    LearningGoalSerializer, ResourceSerializer,
    StudentResourceLogSerializer
)

# ---------------------------
# Authentication Views
# ---------------------------
class StudentLoginView(APIView):
    @swagger_auto_schema(request_body=StudentLoginSerializer)
    def post(self, request):
        try:
            serializer = StudentLoginSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        except Exception as e:
            return Response({"message": "Login failed", "error": str(e)}, status=400)

class StudentRegisterView(generics.CreateAPIView):
    serializer_class = StudentRegisterSerializer

    @swagger_auto_schema(request_body=StudentRegisterSerializer)
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            return Response({
                "message": "Registration successful",
                "refresh": str(refresh),
                "access": str(access),
            })
        except Exception as e:
            return Response({"message": "Registration failed", "error": str(e)}, status=400)

# ---------------------------
# Student Info
# ---------------------------
class StudentInfoView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: StudentInfoSerializer})
    def get(self, request):
        try:
            info = StudentInfo.objects.get(student=request.user)
            serializer = StudentInfoSerializer(info)
            return Response(serializer.data)
        except StudentInfo.DoesNotExist:
            return Response({"message": "Info not found"}, status=404)

    @swagger_auto_schema(request_body=StudentInfoSerializer)
    def post(self, request):
        try:
            serializer = StudentInfoSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(student=request.user)
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        except Exception as e:
            return Response({"message": "Error saving info", "error": str(e)}, status=400)

    @swagger_auto_schema(request_body=StudentInfoSerializer)
    def put(self, request):
        try:
            info = StudentInfo.objects.get(student=request.user)
            serializer = StudentInfoSerializer(info, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except StudentInfo.DoesNotExist:
            return Response({"message": "Info not found"}, status=404)
        except Exception as e:
            return Response({"message": "Update failed", "error": str(e)}, status=400)

    @swagger_auto_schema(auto_schema=None)
    def delete(self, request):
        try:
            info = StudentInfo.objects.get(student=request.user)
            info.delete()
            return Response({"message": "Deleted successfully"})
        except StudentInfo.DoesNotExist:
            return Response({"message": "Info not found"}, status=404)
        except Exception as e:
            return Response({"message": "Delete failed", "error": str(e)}, status=400)

# ---------------------------
# Student Subject Preferences
# ---------------------------
class StudentSubjectListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentSubjectSerializer

    @swagger_auto_schema(responses={200: StudentSubjectSerializer(many=True)})
    def get_queryset(self):
        try:
            return StudentSubject.objects.filter(student=self.request.user)
        except Exception as e:
            raise serializers.ValidationError({"error": f"Query failed: {str(e)}"})

    @swagger_auto_schema(request_body=StudentSubjectSerializer)
    def perform_create(self, serializer):
        try:
            serializer.save(student=self.request.user)
        except Exception as e:
            raise serializers.ValidationError({"error": f"Creation failed: {str(e)}"})

class StudentSubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentSubjectSerializer
    lookup_field = "subject_id"

    def get_queryset(self):
        try:
            return StudentSubject.objects.filter(student=self.request.user)
        except Exception as e:
            raise serializers.ValidationError({"error": f"Lookup failed: {str(e)}"})

# ---------------------------
# Static Subject List
# ---------------------------
class SubjectListView(generics.ListAPIView):
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all()

# ---------------------------
# Quizzes
# ---------------------------
class QuizListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuizSerializer

    def get_queryset(self):
        try:
            return Quiz.objects.filter(student=self.request.user)
        except Exception as e:
            raise serializers.ValidationError({"error": f"Query failed: {str(e)}"})

    @swagger_auto_schema(request_body=QuizSerializer)
    def perform_create(self, serializer):
        try:
            serializer.save(student=self.request.user)
        except Exception as e:
            raise serializers.ValidationError({"error": f"Quiz creation failed: {str(e)}"})

# ---------------------------
# Learning Goals
# ---------------------------
class LearningGoalListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LearningGoalSerializer

    def get_queryset(self):
        try:
            return LearningGoal.objects.filter(student=self.request.user)
        except Exception as e:
            raise serializers.ValidationError({"error": f"Goal fetch failed: {str(e)}"})

    @swagger_auto_schema(request_body=LearningGoalSerializer)
    def perform_create(self, serializer):
        try:
            serializer.save(student=self.request.user)
        except Exception as e:
            raise serializers.ValidationError({"error": f"Goal creation failed: {str(e)}"})

class LearningGoalDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LearningGoalSerializer
    queryset = LearningGoal.objects.all()
    lookup_field = "pk"

    @swagger_auto_schema(operation_summary="Retrieve a learning goal by ID")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(request_body=LearningGoalSerializer, operation_summary="Update a learning goal by ID")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Delete a learning goal by ID")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

# ---------------------------
# Resources
# ---------------------------
class ResourceListView(generics.ListAPIView):
    serializer_class = ResourceSerializer
    queryset = Resource.objects.all()

    @swagger_auto_schema(
        operation_summary="List all learning resources",
        responses={200: ResourceSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

# ---------------------------
# Resource Logs
# ---------------------------
class StudentResourceLogListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentResourceLogSerializer

    def get_queryset(self):
        try:
            return StudentResourceLog.objects.filter(student=self.request.user)
        except Exception as e:
            raise serializers.ValidationError({"error": f"Log fetch failed: {str(e)}"})

    @swagger_auto_schema(request_body=StudentResourceLogSerializer)
    def perform_create(self, serializer):
        try:
            serializer.save(student=self.request.user)
        except Exception as e:
            raise serializers.ValidationError({"error": f"Log creation failed: {str(e)}"})