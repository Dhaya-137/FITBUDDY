from typing import Literal

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


Goal = Literal[
    "weight loss",
    "muscle gain",
    "general wellness",
    "flexibility",
    "endurance",
]


Intensity = Literal[
    "low",
    "medium",
    "high",
]


class UserInput(BaseModel):

    user_id: str = Field(
        min_length=2,
        max_length=80,
    )

    name: str = Field(
        min_length=1,
        max_length=120,
    )

    age: int = Field(
        ge=13,
        le=100,
    )

    weight: float = Field(
        gt=20,
        le=500,
    )

    goal: Goal

    intensity: Intensity

    @field_validator(
        "user_id",
        "name",
    )
    @classmethod
    def strip_text(
        cls,
        value: str,
    ) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Value cannot be blank"
            )

        return value


class FeedbackRequest(BaseModel):

    user_id: str = Field(
        min_length=2,
        max_length=80,
    )

    feedback: str = Field(
        min_length=3,
        max_length=2000,
    )


class UserResponse(BaseModel):

    user_id: str

    name: str

    age: int

    weight: float

    goal: str

    intensity: str

    original_plan: str

    updated_plan: str | None

    feedback: str | None

    nutrition_tip: str

    updated_nutrition_tip: str | None

    model_config = {
        "from_attributes": True
    }