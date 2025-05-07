from rest_framework import serializers, generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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
    StudentResourceLogSerializer, FullStudentDataSerializer
)

# Schema for token responses
token_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(type=openapi.TYPE_STRING),
        'access': openapi.Schema(type=openapi.TYPE_STRING),
        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

# ---------------------------
# Authentication Views
# ---------------------------
class StudentLoginView(APIView):
    @swagger_auto_schema(
        request_body=StudentLoginSerializer,
        responses={
            200: openapi.Response("JWT Token", token_response_schema),
            400: openapi.Response("Bad Request", examples={
                "application/json": {"message": "Login failed", "error": "Invalid credentials"}
            }),
        },
        operation_summary="Student login",
        operation_description="Login a student with email and password to receive JWT access and refresh tokens.",
        tags=["Authentication"]
    )
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

    @swagger_auto_schema(
        request_body=StudentRegisterSerializer,
        responses={
            201: openapi.Response("JWT Token", token_response_schema),
            400: openapi.Response("Bad Request", examples={
                "application/json": {"message": "Registration failed", "error": "Email already exists"}
            }),
        },
        operation_summary="Register a student",
        operation_description="Register a new student using email and password and receive JWT tokens.",
        tags=["Authentication"]
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Registration successful",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=201)
        except Exception as e:
            return Response({"message": "Registration failed", "error": str(e)}, status=400)

# ---------------------------
# Student Info View
# ---------------------------
class StudentInfoView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get student profile info",
        operation_description="Returns onboarding details for the authenticated student.",
        responses={
            200: StudentInfoSerializer,
            404: openapi.Response("Not Found", examples={
                "application/json": {"message": "Info not found"}
            })
        },
        tags=["Student Info"]
    )
    def get(self, request):
        try:
            info = StudentInfo.objects.get(student=request.user)
            serializer = StudentInfoSerializer(info)
            return Response(serializer.data)
        except StudentInfo.DoesNotExist:
            return Response({"message": "Info not found"}, status=404)

    @swagger_auto_schema(
        operation_summary="Create student profile info",
        operation_description="Save onboarding data for the authenticated student.",
        request_body=StudentInfoSerializer,
        responses={
            201: StudentInfoSerializer,
            400: openapi.Response("Validation Error", examples={
                "application/json": {"message": "Validation error", "error": "Field is required"}
            }),
        },
        tags=["Student Info"]
    )
    def post(self, request):
        try:
            serializer = StudentInfoSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(student=request.user)
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        except Exception as e:
            return Response({"message": "Error saving info", "error": str(e)}, status=400)

    @swagger_auto_schema(
        operation_summary="Update student profile info",
        operation_description="Update student onboarding data partially or fully.",
        request_body=StudentInfoSerializer,
        responses={
            200: StudentInfoSerializer,
            400: "Validation failed",
            404: "Info not found"
        },
        tags=["Student Info"]
    )
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

    @swagger_auto_schema(
        operation_summary="Delete student profile info",
        operation_description="Delete the authenticated student's onboarding profile.",
        responses={
            200: openapi.Response("Success", examples={
                "application/json": {"message": "Deleted successfully"}
            }),
            404: "Info not found"
        },
        tags=["Student Info"]
    )
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

    @swagger_auto_schema(
        operation_summary="List student subject preferences",
        operation_description="Returns all subject-specific preferences (favorite/weak topics, goals) for the student.",
        responses={200: StudentSubjectSerializer(many=True)},
        tags=["Subject Preferences"]
    )
    def get_queryset(self):
        try:
            return StudentSubject.objects.filter(student=self.request.user)
        except Exception as e:
            raise serializers.ValidationError({"error": f"Query failed: {str(e)}"})

    @swagger_auto_schema(
        operation_summary="Create subject preference entry",
        operation_description="Saves subject-specific personalization like learning style, favorite/weak topics, goals.",
        request_body=StudentSubjectSerializer,
        responses={201: StudentSubjectSerializer},
        tags=["Subject Preferences"]
    )
    def perform_create(self, serializer):
        try:
            serializer.save()
        except Exception as e:
            raise serializers.ValidationError({"error": f"Creation failed: {str(e)}"})

class StudentSubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentSubjectSerializer
    lookup_field = "subject_id"

    def get_queryset(self):
        return StudentSubject.objects.filter(student=self.request.user)

    @swagger_auto_schema(
        operation_summary="Retrieve a subject preference",
        operation_description="Get subject-specific personalization settings for a student.",
        tags=["Subject Preferences"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=StudentSubjectSerializer,
        operation_summary="Update subject preference",
        operation_description="Update learning style or topic-related personalization for a subject.",
        tags=["Subject Preferences"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete subject preference",
        operation_description="Delete subject-specific personalization for the student.",
        tags=["Subject Preferences"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

# ---------------------------
# Static Subject List
# ---------------------------
class SubjectListView(generics.ListAPIView):
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all()

    @swagger_auto_schema(
        operation_summary="List available subjects",
        operation_description="Returns all subjects available in the system.",
        responses={200: SubjectSerializer(many=True)},
        tags=["Subjects"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# ---------------------------
# Quiz List + Create
# ---------------------------
class QuizListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuizSerializer

    @swagger_auto_schema(
        operation_summary="List quizzes taken by student",
        operation_description="Returns all quizzes attempted or assigned to the authenticated student.",
        responses={200: QuizSerializer(many=True)},
        tags=["Quizzes"]
    )
    def get_queryset(self):
        try:
            return Quiz.objects.filter(student=self.request.user)
        except Exception as e:
            raise serializers.ValidationError({"error": f"Query failed: {str(e)}"})

    @swagger_auto_schema(
        request_body=QuizSerializer,
        operation_summary="Create a new quiz",
        operation_description="Creates a new quiz entry for the student, usually triggered by an agent.",
        responses={201: QuizSerializer},
        tags=["Quizzes"]
    )
    def perform_create(self, serializer):
        try:
            serializer.save()
        except Exception as e:
            raise serializers.ValidationError({"error": f"Quiz creation failed: {str(e)}"})

class AnswerQuizView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Submit answers for a quiz",
        operation_description="Allows a student to submit answers for each question in a quiz. Does not evaluate yet.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["quiz_id", "answers"],
            properties={
                "quiz_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "answers": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    additional_properties=openapi.Schema(type=openapi.TYPE_STRING)
                )
            }
        ),
        tags=["Quiz"]
    )
    def post(self, request):
        try:
            user = request.user
            quiz_id = request.data["quiz_id"]
            answers = request.data["answers"]  # {question_id: student_answer}

            quiz = Quiz.objects.get(id=quiz_id, student=user)

            if quiz.status != "pending":
                return Response({"error": "Quiz has already been submitted or completed."}, status=400)

            for q in quiz.questions.all():
                answer = answers.get(str(q.id))
                if answer:
                    q.student_answer = answer
                    q.save()

            return Response({"message": "Answers submitted successfully."})

        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found."}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

# ---------------------------
# Learning Goal List & Create
# ---------------------------
class LearningGoalListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LearningGoalSerializer

    @swagger_auto_schema(
        operation_summary="List learning goals",
        operation_description="Returns all learning goals set by the authenticated student.",
        responses={200: LearningGoalSerializer(many=True)},
        tags=["Learning Goals"]
    )
    def get_queryset(self):
        try:
            return LearningGoal.objects.filter(student=self.request.user)
        except Exception as e:
            raise serializers.ValidationError({"error": f"Goal fetch failed: {str(e)}"})

    @swagger_auto_schema(
        request_body=LearningGoalSerializer,
        operation_summary="Create a learning goal",
        operation_description="Add a personal learning goal for the student, optionally tied to a subject.",
        responses={201: LearningGoalSerializer},
        tags=["Learning Goals"]
    )
    def perform_create(self, serializer):
        try:
            serializer.save(student=self.request.user)
        except Exception as e:
            raise serializers.ValidationError({"error": f"Goal creation failed: {str(e)}"})


# ---------------------------
# Learning Goal Detail View
# ---------------------------
class LearningGoalDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LearningGoalSerializer
    queryset = LearningGoal.objects.all()
    lookup_field = "pk"

    @swagger_auto_schema(
        operation_summary="Retrieve a learning goal",
        operation_description="Returns a specific learning goal for the authenticated student.",
        tags=["Learning Goals"]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=LearningGoalSerializer,
        operation_summary="Update a learning goal",
        operation_description="Update text, subject, or status of a learning goal.",
        tags=["Learning Goals"]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a learning goal",
        operation_description="Delete a specific learning goal.",
        tags=["Learning Goals"]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

# ---------------------------
# Learning Resources (List Only)
# ---------------------------
class ResourceListView(generics.ListAPIView):
    serializer_class = ResourceSerializer
    queryset = Resource.objects.all()

    @swagger_auto_schema(
        operation_summary="List recommended resources",
        operation_description="Returns all recommended learning resources (e.g. videos, articles, LeetCode links).",
        responses={200: ResourceSerializer(many=True)},
        tags=["Resources"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# ---------------------------
# Student Resource Logs (List, Create)
# ---------------------------
class StudentResourceLogListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentResourceLogSerializer

    @swagger_auto_schema(
        operation_summary="List resource usage logs",
        operation_description="Returns a list of all resources accessed by the student.",
        responses={200: StudentResourceLogSerializer(many=True)},
        tags=["Resource Logs"]
    )
    def get_queryset(self):
        try:
            return StudentResourceLog.objects.filter(student=self.request.user)
        except Exception as e:
            raise serializers.ValidationError({"error": f"Log fetch failed: {str(e)}"})

    @swagger_auto_schema(
        request_body=StudentResourceLogSerializer,
        operation_summary="Log a resource access",
        operation_description="Logs that a student accessed a specific resource, optionally with feedback.",
        responses={201: StudentResourceLogSerializer},
        tags=["Resource Logs"]
    )
    def perform_create(self, serializer):
        try:
            serializer.save(student=self.request.user)
        except Exception as e:
            raise serializers.ValidationError({"error": f"Log creation failed: {str(e)}"})
        
# ---------------------------
# List All Student Data
# ---------------------------
class StudentProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get full student profile",
        operation_description="Returns all information about the authenticated student in a single JSON response.",
        responses={200: FullStudentDataSerializer},
        tags=["Student"]
    )
    def get(self, request):
        user = request.user
        try:
            info = StudentInfo.objects.filter(student=user).first()
            subjects = StudentSubject.objects.filter(student=user)
            goals = LearningGoal.objects.filter(student=user)
            resource_logs = StudentResourceLog.objects.filter(student=user)

            if not info and not subjects.exists() and not goals.exists() and not resource_logs.exists():
                return Response({"message": "No data found for this student."}, status=200)

            serializer = FullStudentDataSerializer(
                user,
                context={
                    "request": request,
                    "student": user,
                    "info": info,
                    "subjects": subjects,
                    "goals": goals,
                    "resource_logs": resource_logs,
                }
            )

            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)