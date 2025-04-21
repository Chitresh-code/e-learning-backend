import os
from decouple import config
from openai import OpenAI
from ai.utils.schemas import ResourceResponse

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or config("OPENAI_API_KEY"))

def generate_resource_suggestions(student_profile: dict, learning_plan: dict) -> ResourceResponse:
    prompt = f"""
You are a smart education assistant. Recommend high-quality learning resources for the student
based on their preferences and the given learning plan.

Student Info: {student_profile}
Learning Plan: {learning_plan}

Return only structured resources with title, type, URL, and a brief description.
"""

    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an education assistant that returns structured JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format=ResourceResponse,
    )

    return completion.choices[0].message.parsed