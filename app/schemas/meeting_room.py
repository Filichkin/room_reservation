from typing import Optional

from pydantic import BaseModel, Field, field_validator


class MeetingRoomBase(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str]


class MeetingRoomCreate(MeetingRoomBase):
    # Переопределяем атрибут name, делаем его обязательным.
    name: str = Field(..., min_length=1, max_length=100)

    @field_validator('name')
    def name_validator(cls, value: str):
        if not value:
            raise ValueError('Имя не должно быть пустым')
        return value


class MeetingRoomDB(MeetingRoomCreate):
    id: int

    class Config:
        orm_mode = True
