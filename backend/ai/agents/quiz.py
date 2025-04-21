from openai import OpenAI
from decouple import config
from pydantic import BaseModel
from typing import List
from ai.utils.schemas import QuizGenerationResponse, EvaluationResult

client = OpenAI(api_key=config("OPENAI_API_KEY"))


def generate_quiz(subject: str, topic: str, level: str) -> QuizGenerationResponse:
    prompt = f"""
Generate 10 multiple-choice questions on the topic '{topic}' from subject '{subject}' at '{level}' level.
Provide options as a dictionary like: {{"A": "...", "B": "...", "C": "...", "D": "..."}}
Mark the correct option key only.
"""

    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a quiz generator that returns structured questions only."},
            {"role": "user", "content": prompt}
        ],
        response_format=QuizGenerationResponse
    )

    return completion.choices[0].message.parsed

def evaluate_quiz(quiz_data: List[dict]) -> EvaluationResult:
    prompt = f"""
Evaluate the following quiz attempt. For each question, check if the student's answer is correct.
Return total score out of 100, detailed feedback, and correctness per question.

{quiz_data}
"""

    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an AI quiz evaluator."},
            {"role": "user", "content": prompt}
        ],
        response_format=EvaluationResult
    )

    return completion.choices[0].message.parsed