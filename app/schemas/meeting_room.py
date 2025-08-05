from typing import Optional

from pydantic import BaseModel, Field, field_validator


class MeetingRoomCreate(BaseModel):
    name: str = Field(
        ...,
        max_length=100,
    )
    description: Optional[str]

    @field_validator('name')
    def name_validator(cls, value: str):
        if not value:
            raise ValueError('Имя не должно быть пустым')
        return value
