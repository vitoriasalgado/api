from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.mentor import Mentor


class MentorCreate(BaseModel):
    name: str = Field(min_length=1)
    expertise: str = Field(min_length=1)
    bio: str | None = None


class MentorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    expertise: str | None = Field(default=None, min_length=1)
    bio: str | None = None


class MentorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    expertise: str
    bio: str | None


DbSession = Annotated[AsyncSession, Depends(get_db)]

router = APIRouter(tags=["mentors"])


@router.post("/mentors", status_code=201, response_model=MentorRead)
async def create_mentor(payload: MentorCreate, db: DbSession) -> Mentor:
    mentor = Mentor(
        name=payload.name,
        expertise=payload.expertise,
        bio=payload.bio,
    )
    db.add(mentor)
    await db.commit()
    await db.refresh(mentor)
    return mentor


@router.get("/mentors", response_model=list[MentorRead])
async def list_mentors(db: DbSession) -> list[Mentor]:
    result = await db.execute(select(Mentor))
    return list(result.scalars().all())


@router.get("/mentors/{id}", response_model=MentorRead)
async def get_mentor(id: int, db: DbSession) -> Mentor:
    mentor = await db.get(Mentor, id)
    if mentor is None:
        raise HTTPException(status_code=404, detail="Mentor not found")
    return mentor


@router.patch("/mentors/{id}", response_model=MentorRead)
async def update_mentor(id: int, payload: MentorUpdate, db: DbSession) -> Mentor:
    mentor = await db.get(Mentor, id)
    if mentor is None:
        raise HTTPException(status_code=404, detail="Mentor not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(mentor, key, value)

    await db.commit()
    await db.refresh(mentor)
    return mentor


@router.delete("/mentors/{id}", status_code=204)
async def delete_mentor(id: int, db: DbSession) -> None:
    mentor = await db.get(Mentor, id)
    if mentor is None:
        raise HTTPException(status_code=404, detail="Mentor not found")
    await db.delete(mentor)
    await db.commit()
