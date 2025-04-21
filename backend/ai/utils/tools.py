from ai.utils.schemas import UpdateLearningPlanRequest

def apply_learning_plan_updates(data: UpdateLearningPlanRequest):
    from learningplan.models import LearningPlan, LearningPlanWeek
    from student.models import Student

    student = Student.objects.get(email=data.student_email)
    plan = LearningPlan.objects.filter(student=student).order_by("-created_at").first()

    for update in data.updates:
        week_obj = LearningPlanWeek.objects.get(plan=plan, week=update.week)
        week_obj.focus_topics = update.focus_topics
        week_obj.practice_tasks = update.practice_tasks
        week_obj.ai_message = update.ai_message
        week_obj.save()

    return {"message": "Learning plan updated successfully."}