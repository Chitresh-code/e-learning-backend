from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from student.models import StudentInfo, StudentSubject, LearningGoal, StudentResourceLog
from learningplan.models import LearningPlan
from .models import AgentInteractionLog
from student.serializers import FullStudentDataSerializer
from ai.agents.ui_agent import interact_with_student
from ai.agents.quiz import generate_quiz, evaluate_quiz
from student.models import Quiz, Question, Subject

class ChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Chat with learning assistant",
        operation_description="Interacts with the student using previous learning plan and context, and returns updated info if needed.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"message": openapi.Schema(type=openapi.TYPE_STRING)}
        ),
        tags=["Learning Assistant"]
    )
    def post(self, request):
        user = request.user
        try:
            message = request.data.get("message")
            if not message:
                return Response({"error": "Message is required."}, status=400)

            info = StudentInfo.objects.get(student=user)
            subjects = StudentSubject.objects.filter(student=user)
            goals = LearningGoal.objects.filter(student=user)
            resource_logs = StudentResourceLog.objects.filter(student=user)

            student_data = FullStudentDataSerializer(user, context={
                "request": request,
                "student": user,
                "info": info,
                "subjects": subjects,
                "goals": goals,
                "resource_logs": resource_logs,
            }).data

            plan = LearningPlan.objects.filter(student=user).order_by("-created_at").first()
            plan_data = {
                "student": user.email,
                "plan_duration_weeks": plan.plan_duration_weeks,
                "weekly_plan": [
                    {
                        "week": w.week,
                        "focus_topics": w.focus_topics,
                        "practice_tasks": w.practice_tasks,
                        "ai_message": w.ai_message
                    }
                    for w in plan.weeks.all()
                ] if plan else []
            }

            past_chats = AgentInteractionLog.objects.filter(student=user).order_by("-created_at")[:5]
            chat_context = [
                {"role": "user", "content": c.user_message} if i % 2 == 0 else {"role": "assistant", "content": c.agent_response}
                for i, c in enumerate(reversed(past_chats))
            ]

            response = interact_with_student(student_data, plan_data, message, chat_context)

            AgentInteractionLog.objects.create(
                student=user,
                user_message=message,
                agent_response=response
            )

            return Response({"response": response})

        except Exception as e:
            return Response({"error": str(e)}, status=400)
        
class GenerateAndSaveQuizView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Generate and save a quiz",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["subject", "topic", "level"],
            properties={
                "subject": openapi.Schema(type=openapi.TYPE_STRING),
                "topic": openapi.Schema(type=openapi.TYPE_STRING),
                "level": openapi.Schema(type=openapi.TYPE_STRING, enum=["beginner", "intermediate", "advanced"])
            }
        ),
        tags=["Quiz"]
    )
    def post(self, request):
        try:
            subject_name = request.data["subject"]
            topic = request.data["topic"]
            level = request.data["level"]
            user = request.user

            subject, _ = Subject.objects.get_or_create(name=subject_name)
            result = generate_quiz(subject_name, topic, level)

            quiz = Quiz.objects.create(
                student=user,
                subject=subject,
                total_marks=10 * 1,  # Assuming 1 mark per question
                status="pending"
            )

            for q in result.questions:
                Question.objects.create(
                    quiz=quiz,
                    question_text=q.question_text,
                    options={opt.key: opt.value for opt in q.options},
                    correct_option=q.correct_option
                )

            return Response({"message": "Quiz created successfully.", "quiz_id": quiz.id})

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class EvaluateQuizView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Evaluate a quiz",
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
            quiz_id = request.data["quiz_id"]
            answers = request.data["answers"]  # {question_id: student_answer}

            quiz = Quiz.objects.get(id=quiz_id, student=request.user)
            questions = quiz.questions.all()

            quiz_data = []
            correct_count = 0
            for q in questions:
                ans = answers.get(str(q.id))
                is_correct = ans == q.correct_option
                q.student_answer = ans
                q.is_correct = is_correct
                q.save()

                if is_correct:
                    correct_count += 1

                quiz_data.append({
                    "question_text": q.question_text,
                    "correct_option": q.correct_option,
                    "student_answer": ans or "",
                    "is_correct": is_correct
                })

            evaluation = evaluate_quiz(quiz_data)

            quiz.score = evaluation.score
            quiz.ai_feedback = evaluation.feedback
            quiz.status = "completed"
            quiz.save()

            return Response({
                "message": "Quiz evaluated successfully.",
                "score": quiz.score,
                "feedback": quiz.ai_feedback
            })

        except Exception as e:
            return Response({"error": str(e)}, status=400)