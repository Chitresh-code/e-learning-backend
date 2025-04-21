from pydantic import BaseModel, Field
from typing import List, Dict

class WeekPlan(BaseModel):
    week: int
    focus_topics: List[str]
    recommended_resources: List[str]
    practice_tasks: List[str]
    ai_message: str

class LearningPlanSchema(BaseModel):
    student: str
    plan_duration_weeks: int
    weekly_plan: List[WeekPlan]
    
class ResourceItem(BaseModel):
    topic_name: str
    type: str  # e.g., "video", "article", "leetcode", etc.
    url: str
    description: str
    
class ResourceResponse(BaseModel):
    suggestions: List[ResourceItem]
    
class UpdateWeek(BaseModel):
    week: int
    focus_topics: List[str]
    practice_tasks: List[str]
    ai_message: str

class UpdateLearningPlanRequest(BaseModel):
    student_email: str
    updates: List[UpdateWeek]
    
class Option(BaseModel):
    key: str
    value: str

class QuizQuestion(BaseModel):
    question_text: str
    options: List[Option]
    correct_option: str
    
class QuizGenerationResponse(BaseModel):
    questions: List[QuizQuestion]
    
class EvaluatedQuestion(BaseModel):
    question_text: str
    correct_option: str
    student_answer: str
    is_correct: bool

class EvaluationResult(BaseModel):
    score: float
    feedback: str
    evaluated_questions: List[EvaluatedQuestion]