from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from student.models import StudentInfo, StudentSubject, LearningGoal, StudentResourceLog, Resource
from .models import LearningPlan, LearningPlanWeek, LearningPlanResource
from student.serializers import FullStudentDataSerializer
from ai.agents.planner import generate_learning_plan
from ai.agents.resource_generator import generate_resource_suggestions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import json

class GenerateLearningPlanView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Generate learning plan",
        operation_description="Generates and saves a structured weekly learning plan for the authenticated student using their full profile."
                              " (Resources will be generated separately)",
        responses={200: openapi.Response("Plan generated and saved")},
        tags=["Learning Plan"]
    )
    def post(self, request):
        user = request.user
        try:
            info = StudentInfo.objects.get(student=user)
            subjects = StudentSubject.objects.filter(student=user)
            goals = LearningGoal.objects.filter(student=user)
            resource_logs = StudentResourceLog.objects.filter(student=user)

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

            parsed_plan = generate_learning_plan(serializer.data)

            plan = LearningPlan.objects.create(
                student=user,
                plan_duration_weeks=parsed_plan.plan_duration_weeks
            )

            for week_data in parsed_plan.weekly_plan:
                LearningPlanWeek.objects.create(
                    plan=plan,
                    week=week_data.week,
                    focus_topics=week_data.focus_topics,
                    practice_tasks=week_data.practice_tasks,
                    ai_message=week_data.ai_message
                )

            return Response({"message": "Plan generated and saved successfully."})

        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @swagger_auto_schema(
        operation_summary="Get latest learning plan",
        operation_description="Returns the most recent structured learning plan for the authenticated student.",
        responses={200: openapi.Response("Latest learning plan with all weeks")},
        tags=["Learning Plan"]
    )
    def get(self, request):
        try:
            user = request.user
            plan = LearningPlan.objects.filter(student=user).order_by("-created_at").first()

            if not plan:
                return Response({"message": "No learning plan found."}, status=404)

            weeks = plan.weeks.all().order_by("week")
            weekly_data = [
                {
                    "week": w.week,
                    "focus_topics": w.focus_topics,
                    "practice_tasks": w.practice_tasks,
                    "ai_message": w.ai_message
                } for w in weeks
            ]

            return Response({
                "student": user.email,
                "plan_duration_weeks": plan.plan_duration_weeks,
                "weekly_plan": weekly_data,
                "created_at": plan.created_at
            })

        except Exception as e:
            return Response({"error": str(e)}, status=400)

class GenerateResourcesView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Generate learning resources",
        operation_description="Generates personalized learning resources based on the student's preferences and learning plan.",
        responses={200: openapi.Response("Resources generated and saved.")},
        tags=["Learning Resources"]
    )
    def post(self, request):
        try:
            user = request.user
            info = StudentInfo.objects.get(student=user)
            subjects = StudentSubject.objects.filter(student=user)
            goals = LearningGoal.objects.filter(student=user)
            resource_logs = StudentResourceLog.objects.filter(student=user)

            profile_serializer = FullStudentDataSerializer(user, context={
                "request": request,
                "student": user,
                "info": info,
                "subjects": subjects,
                "goals": goals,
                "resource_logs": resource_logs,
            })

            latest_plan = LearningPlan.objects.filter(student=user).order_by("-created_at").first()
            if not latest_plan:
                return Response({"error": "No learning plan found."}, status=400)

            plan_data = {
                "student": user.email,
                "plan_duration_weeks": latest_plan.plan_duration_weeks,
                "weekly_plan": [
                    {
                        "week": w.week,
                        "focus_topics": w.focus_topics,
                        "practice_tasks": w.practice_tasks,
                        "ai_message": w.ai_message
                    }
                    for w in latest_plan.weeks.all()
                ]
            }

            suggestions = generate_resource_suggestions(profile_serializer.data, plan_data)

            for res in suggestions.suggestions:
                Resource.objects.create(
                    topic_name=res.topic_name,
                    subject=subjects.first().subject,  # Best guess
                    url=res.url,
                    type=res.type,
                    description=res.description
                )

            return Response({"message": "Resources generated and saved successfully."})

        except Exception as e:
            return Response({"error": str(e)}, status=400)