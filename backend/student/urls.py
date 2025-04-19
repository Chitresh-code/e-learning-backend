from django.urls import path
from .views import (
    StudentLoginView, StudentRegisterView, StudentInfoView,
    StudentSubjectListCreateView, StudentSubjectDetailView,
    SubjectListView, QuizListCreateView,
    LearningGoalListCreateView, LearningGoalDetailView,
    ResourceListView, StudentResourceLogListCreateView
)

urlpatterns = [
    # Authentication
    path("login/", StudentLoginView.as_view(), name="student-login"),
    path("register/", StudentRegisterView.as_view(), name="student-register"),

    # Student onboarding info
    path("info/", StudentInfoView.as_view(), name="student-info"),

    # Student's subject preferences
    path("subject/", StudentSubjectListCreateView.as_view(), name="student-subjects"),
    path("subject/<int:subject_id>/", StudentSubjectDetailView.as_view(), name="student-subject-detail"),

    # Global subject list (used by agents/frontend)
    path("subjects/", SubjectListView.as_view(), name="subjects"),

    # Quizzes
    path("quizzes/", QuizListCreateView.as_view(), name="quizzes"),

    # Learning Goals
    path("goals/", LearningGoalListCreateView.as_view(), name="learning-goals"),
    path("goals/<int:pk>/", LearningGoalDetailView.as_view(), name="goal-detail"),

    # Resource catalog and student logs
    path("resources/", ResourceListView.as_view(), name="resources"),
    path("resource-log/", StudentResourceLogListCreateView.as_view(), name="resource-log"),
]