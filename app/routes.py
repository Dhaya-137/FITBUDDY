from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi import Request
from fastapi import status

from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates

from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .gemini_client import GeminiConfigurationError
from .gemini_flash_generator import (
    generate_nutrition_tip_with_flash,
)
from .gemini_generator import (
    generate_workout_gemini,
)
from .models import User
from .schemas import FeedbackRequest
from .schemas import UserInput
from .schemas import UserResponse
from .updated_plan import update_workout_plan


templates = Jinja2Templates(
    directory="templates"
)


router = APIRouter()


GOALS = [
    "weight loss",
    "muscle gain",
    "general wellness",
    "flexibility",
    "endurance",
]


INTENSITIES = [
    "low",
    "medium",
    "high",
]


def render_error(
    request: Request,
    message: str,
    status_code: int = 500,
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "error": message,
            "goals": GOALS,
            "intensities": INTENSITIES,
        },
        status_code=status_code,
    )


def find_user(
    db: Session,
    user_id: str,
) -> User | None:

    return db.scalar(
        select(User).where(
            User.user_id == user_id
        )
    )


@router.get(
    "/",
    response_class=HTMLResponse,
)
def home(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "goals": GOALS,
            "intensities": INTENSITIES,
        },
    )


@router.post(
    "/generate-workout",
    response_class=HTMLResponse,
)
def generate_workout_form(

    request: Request,

    user_id: str = Form(...),

    name: str = Form(...),

    age: int = Form(...),

    weight: float = Form(...),

    goal: str = Form(...),

    intensity: str = Form(...),

    db: Session = Depends(get_db),
):

    try:

        data = UserInput(
            user_id=user_id,
            name=name,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

    except Exception as exc:

        return render_error(
            request,
            f"Please check your inputs: {exc}",
            422,
        )

    try:

        workout_plan = generate_workout_gemini(
            name=data.name,
            age=data.age,
            weight=data.weight,
            goal=data.goal,
            intensity=data.intensity,
        )

        nutrition_tip = (
            generate_nutrition_tip_with_flash(
                goal=data.goal,
                intensity=data.intensity,
            )
        )

    except GeminiConfigurationError as exc:

        return render_error(
            request,
            str(exc),
            503,
        )

    except Exception as exc:

        return render_error(
            request,
            (
                "AI generation failed. "
                "Check your Gemini API key/model "
                f"configuration. Details: {exc}"
            ),
            502,
        )

    user = find_user(
        db,
        data.user_id,
    )

    if user:

        user.name = data.name
        user.age = data.age
        user.weight = data.weight
        user.goal = data.goal
        user.intensity = data.intensity

        user.original_plan = workout_plan

        user.updated_plan = None
        user.feedback = None

        user.nutrition_tip = nutrition_tip

        user.updated_nutrition_tip = None

    else:

        user = User(

            user_id=data.user_id,

            name=data.name,

            age=data.age,

            weight=data.weight,

            goal=data.goal,

            intensity=data.intensity,

            original_plan=workout_plan,

            nutrition_tip=nutrition_tip,
        )

        db.add(user)

    db.commit()

    db.refresh(user)

    return templates.TemplateResponse(
        request=request,

        name="result.html",

        context={
            "user": user,
            "workout_plan": workout_plan,
            "nutrition_tip": nutrition_tip,
            "is_updated": False,
            "success": (
                "Your personalized plan "
                "has been generated."
            ),
        },
    )


@router.post(
    "/submit-feedback",
    response_class=HTMLResponse,
)
def submit_feedback_form(

    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...),

    db: Session = Depends(get_db),
):

    user = find_user(
        db,
        user_id,
    )

    if not user:

        return render_error(
            request,
            "User ID not found. Generate a plan first.",
            404,
        )

    if not feedback.strip():

        return render_error(
            request,
            "Please enter feedback before submitting.",
            422,
        )

    try:

        revised = update_workout_plan(

            original_plan=user.original_plan,

            feedback=feedback.strip(),

            name=user.name,

            age=user.age,

            weight=user.weight,

            goal=user.goal,

            intensity=user.intensity,
        )

        revised_tip = (
            generate_nutrition_tip_with_flash(
                goal=user.goal,
                intensity=user.intensity,
            )
        )

    except GeminiConfigurationError as exc:

        return render_error(
            request,
            str(exc),
            503,
        )

    except Exception as exc:

        return render_error(
            request,
            f"AI update failed: {exc}",
            502,
        )

    user.feedback = feedback.strip()

    user.updated_plan = revised

    user.updated_nutrition_tip = revised_tip

    db.commit()

    db.refresh(user)

    return templates.TemplateResponse(
        request=request,

        name="result.html",

        context={
            "user": user,
            "workout_plan": revised,
            "nutrition_tip": revised_tip,
            "is_updated": True,
            "success": (
                "Your plan was updated "
                "using your feedback."
            ),
        },
    )


@router.get(
    "/view-all-users",
    response_class=HTMLResponse,
)
def view_all_users(

    request: Request,

    token: str | None = None,

    db: Session = Depends(get_db),
):

    if (
        settings.admin_token
        and token != settings.admin_token
    ):

        return HTMLResponse(
            "Unauthorized",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    users = db.scalars(
        select(User).order_by(
            User.created_at.desc()
        )
    ).all()

    return templates.TemplateResponse(

        request=request,

        name="all_users.html",

        context={
            "users": users,
            "admin_protected": bool(
                settings.admin_token
            ),
        },
    )


@router.delete(
    "/api/users/{user_id}",
    status_code=204,
)
def delete_user(

    user_id: str,

    token: str | None = None,

    db: Session = Depends(get_db),
):

    if (
        settings.admin_token
        and token != settings.admin_token
    ):

        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

    user = find_user(
        db,
        user_id,
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    db.delete(user)

    db.commit()


@router.get(
    "/api/health"
)
def health():

    return {
        "status": "ok",
        "app": settings.app_name,
    }


@router.post(
    "/api/generate-workout",
    response_model=UserResponse,
)
def api_generate_workout(

    data: UserInput,

    db: Session = Depends(get_db),
):

    try:

        workout_plan = generate_workout_gemini(

            name=data.name,

            age=data.age,

            weight=data.weight,

            goal=data.goal,

            intensity=data.intensity,
        )

        nutrition_tip = (
            generate_nutrition_tip_with_flash(
                goal=data.goal,
                intensity=data.intensity,
            )
        )

    except GeminiConfigurationError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=(
                f"AI generation failed: {exc}"
            ),
        ) from exc

    user = find_user(
        db,
        data.user_id,
    )

    if not user:

        user = User(

            user_id=data.user_id,

            name=data.name,

            age=data.age,

            weight=data.weight,

            goal=data.goal,

            intensity=data.intensity,

            original_plan=workout_plan,

            nutrition_tip=nutrition_tip,
        )

        db.add(user)

    else:

        user.name = data.name
        user.age = data.age
        user.weight = data.weight
        user.goal = data.goal
        user.intensity = data.intensity

        user.original_plan = workout_plan

        user.updated_plan = None
        user.feedback = None

        user.nutrition_tip = nutrition_tip

        user.updated_nutrition_tip = None

    db.commit()

    db.refresh(user)

    return user


@router.post(
    "/api/submit-feedback",
    response_model=UserResponse,
)
def api_submit_feedback(

    data: FeedbackRequest,

    db: Session = Depends(get_db),
):

    user = find_user(
        db,
        data.user_id,
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    try:

        user.updated_plan = (
            update_workout_plan(

                original_plan=user.original_plan,

                feedback=data.feedback,

                name=user.name,

                age=user.age,

                weight=user.weight,

                goal=user.goal,

                intensity=user.intensity,
            )
        )

        user.updated_nutrition_tip = (
            generate_nutrition_tip_with_flash(
                goal=user.goal,
                intensity=user.intensity,
            )
        )

    except GeminiConfigurationError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=f"AI update failed: {exc}",
        ) from exc

    user.feedback = data.feedback

    db.commit()

    db.refresh(user)

    return user


@router.get(
    "/api/users/{user_id}",
    response_model=UserResponse,
)
def api_get_user(

    user_id: str,

    db: Session = Depends(get_db),
):

    user = find_user(
        db,
        user_id,
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user