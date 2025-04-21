import os
from decouple import config
from openai import OpenAI
from ai.utils.schemas import LearningPlanSchema

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or config("OPENAI_API_KEY"))

def generate_learning_plan(student_profile: dict) -> LearningPlanSchema:
    email = student_profile.get("email", "unknown@student.com")
    goals = student_profile.get("goals", [])
    subjects = student_profile.get("subjects", [])
    info = student_profile.get("info", {})
    quizzes = student_profile.get("quizzes", [])
    resource_logs = student_profile.get("resource_logs", [])

    user_prompt = f"""
Generate a structured weekly learning plan using the following data:

- Email: {email}
- Info: {info}
- Subjects: {subjects}
- Goals: {goals}
- Quizzes: {quizzes}
- Resource Logs: {resource_logs}

Return only focus topics, practice tasks, and AI motivational messages per week.
Do NOT include any resources in the output.
Ensure the response matches the structured schema exactly.
"""

    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an educational planning assistant that returns structured JSON only."},
            {"role": "user", "content": user_prompt}
        ],
        response_format=LearningPlanSchema,
    )

    return completion.choices[0].message.parsed