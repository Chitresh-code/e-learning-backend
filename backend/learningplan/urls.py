from .views import GenerateResourcesView, GenerateLearningPlanView
from django.urls import path

urlpatterns = [
    path("resources/", GenerateResourcesView.as_view(), name="generate-resources"),
    path("learning-plan/", GenerateLearningPlanView.as_view(), name="generate-learning-plan"),
]