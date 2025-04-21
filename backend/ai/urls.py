from django.urls import path
from .views import ChatAPIView, EvaluateQuizView, GenerateAndSaveQuizView

urlpatterns = [
    path("chat/", ChatAPIView.as_view(), name="chat-with-learning-assistant"),
    path("quiz/generate/", GenerateAndSaveQuizView.as_view(), name="generate-quiz"),
    path("quiz/evaluate/", EvaluateQuizView.as_view(), name="evaluate-quiz")
]
