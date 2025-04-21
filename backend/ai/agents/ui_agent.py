from openai import OpenAI
from decouple import config
from ai.utils.tools import apply_learning_plan_updates
from ai.utils.schemas import UpdateLearningPlanRequest

client = OpenAI(api_key=config("OPENAI_API_KEY"))

def interact_with_student(student_data: dict, learning_plan: dict, user_message: str, chat_context: list) -> str:
    # Compose the full message list: system → context → prior chat → new user message
    messages = [
        {"role": "system", "content": "You are an interactive learning assistant. Help the student improve their plan."},
        {"role": "user", "content": f"Student profile: {student_data}\nLearning Plan: {learning_plan}"}
    ] + chat_context + [
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "update_learning_plan",
                    "description": "Update the student's learning plan based on feedback",
                    "parameters": UpdateLearningPlanRequest.model_json_schema()

                }
            }
        ],
        tool_choice="auto"
    )

    msg = response.choices[0].message

    if msg.tool_calls:
        for tool_call in msg.tool_calls:
            if tool_call.function.name == "update_learning_plan":
                args = UpdateLearningPlanRequest.model_validate_json(tool_call.function.arguments)
                return apply_learning_plan_updates(args)
    else:
        return msg.content