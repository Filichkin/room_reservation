from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meeting_room import MeetingRoom
from app.schemas.meeting_room import MeetingRoomCreate


async def create_meeting_room(
        new_room: MeetingRoomCreate,
        session: AsyncSession,
) -> MeetingRoom:
    # Конвертируем объект MeetingRoomCreate в словарь.
    new_room_data = new_room.model_dump()

    # Создаём объект модели MeetingRoom.
    # В параметры передаём пары "ключ=значение",
    # для этого распаковываем словарь.
    db_room = MeetingRoom(**new_room_data)

    session.add(db_room)
    await session.commit()
    await session.refresh(db_room)
    return db_room


async def get_room_id_by_name(
        room_name: str,
        session: AsyncSession
) -> Optional[int]:
    db_room_id = await session.execute(
        select(MeetingRoom.id).where(
            MeetingRoom.name == room_name
        )
    )
    db_room_id = db_room_id.scalars().first()
    return db_room_id


async def read_all_rooms_from_db(session: AsyncSession) -> List[MeetingRoom]:
    result = await session.execute(select(MeetingRoom))
    rooms = result.scalars().all()
    return rooms
