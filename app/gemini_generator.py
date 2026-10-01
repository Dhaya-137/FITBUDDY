from .config import settings
from .gemini_client import generate_text


def generate_workout_gemini(
    *,
    name: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
) -> str:

    prompt = f"""
You are FitBuddy, an AI fitness-planning assistant.

Create a personalized 7-day fitness plan.

USER PROFILE
------------
Name: {name}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Preferred intensity: {intensity}

PLAN REQUIREMENTS
-----------------
1. Create exactly 7 labeled days:
   Day 1, Day 2, Day 3, Day 4, Day 5, Day 6, Day 7.

2. Every day must contain:
   - Focus
   - Warm-up
   - Main workout
   - Rest guidance
   - Cooldown/recovery

3. For the main workout, provide exercises with:
   - Sets and repetitions, OR
   - Duration where appropriate.

4. Match the workout difficulty to the requested intensity.

5. Include appropriate rest/recovery.

6. Use practical exercises that can be performed
   with common gym or home equipment.

7. Make the plan clear and easy to follow.

8. Do not prescribe medication.

9. Do not diagnose medical conditions.

10. Do not recommend dangerous or extreme training.

11. Do not recommend extreme calorie restriction.

12. Do not make medical claims.

13. Do not use JSON.

14. Use plain text with clear headings.

15. End with a short Safety Note.

IMPORTANT:
This is a general wellness planning tool and is not a
substitute for advice from a qualified healthcare,
nutrition, or fitness professional.
"""

    return generate_text(
        settings.gemini_pro_model,
        prompt,
        max_output_tokens=6000,
    )