from .config import settings
from .gemini_client import generate_text


def update_workout_plan(
    *,
    original_plan: str,
    feedback: str,
    name: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
) -> str:

    prompt = f"""
You are updating an existing FitBuddy 7-day fitness plan.

User:

Name:
{name}

Age:
{age}

Weight:
{weight} kg

Goal:
{goal}

Intensity:
{intensity}


Original plan:

---BEGIN ORIGINAL PLAN---

{original_plan}

---END ORIGINAL PLAN---


User feedback:

---BEGIN FEEDBACK---

{feedback}

---END FEEDBACK---


Create a revised 7-day plan that incorporates reasonable
user feedback.

Preserve useful parts of the original plan when they do
not conflict with the feedback.

Requirements:

- Exactly 7 labeled days.
- Each day has Focus.
- Each day has Warm-up.
- Each day has Main workout.
- Each day has Rest guidance.
- Each day has Cooldown/recovery.
- Include rest/recovery appropriately.
- Do not diagnose conditions.
- Do not prescribe medical treatment.
- Do not recommend dangerous exercise volume.
- Do not recommend extreme dieting.
- Plain text.
- Easy to scan.
- End with a short Safety note.
"""

    return generate_text(
        settings.gemini_pro_model,
        prompt,
        max_output_tokens=6000,
    )