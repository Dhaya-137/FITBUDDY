from .config import settings
from .gemini_client import generate_text


def generate_nutrition_tip_with_flash(
    *,
    goal: str,
    intensity: str,
) -> str:

    prompt = f"""
You are FitBuddy's nutrition and recovery assistant.

Goal:
{goal}

Workout intensity:
{intensity}

Give one concise, practical nutrition OR recovery tip
that complements the user's goal.

Prefer sustainable habits such as:

- adequate protein
- hydration
- balanced meals
- fiber-rich foods
- sleep
- recovery

Do not prescribe supplements.

Do not prescribe medical treatments.

Do not provide extreme calorie targets.

Keep the answer under 120 words.

Mention that individual nutrition needs vary when relevant.
"""

    return generate_text(
        settings.gemini_flash_model,
        prompt,
        max_output_tokens=300,
    )