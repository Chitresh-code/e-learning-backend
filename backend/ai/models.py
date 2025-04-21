from django.db import models

class AgentInteractionLog(models.Model):
    student = models.ForeignKey("student.Student", on_delete=models.CASCADE)
    user_message = models.TextField()
    agent_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interaction with {self.student.email} at {self.created_at}"