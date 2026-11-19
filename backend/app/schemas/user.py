import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    email: str
    xp: int
    current_streak: int
    created_at: datetime


class UserUpdate(BaseModel):
    username: str = Field(min_length=2, max_length=30)

    @field_validator("username")
    @classmethod
    def _validate_username(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("username is required")
        if not value.replace("_", "").replace("-", "").isalnum():
            raise ValueError("username may only contain letters, numbers, - and _")
        return value
