from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.pagination import Page
from app.db.session import get_db
from app.models.materia import Materia
from app.models.mentor import Mentor


class MentorCreate(BaseModel):
    name: str = Field(min_length=1)
    expertise: str = Field(min_length=1)
    bio: str | None = None
    materia_id: int | None = None


class MentorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    expertise: str | None = Field(default=None, min_length=1)
    bio: str | None = None
    materia_id: int | None = None


class MentorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    expertise: str
    bio: str | None
    materia_id: int | None


class MateriaNested(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


DbSession = Annotated[AsyncSession, Depends(get_db)]

router = APIRouter(tags=["mentors"])


@router.post("/mentors", status_code=201, response_model=MentorRead)
async def create_mentor(payload: MentorCreate, db: DbSession) -> Mentor:
    if payload.materia_id is not None and await db.get(Materia, payload.materia_id) is None:
        raise HTTPException(status_code=404, detail="Materia not found")

    mentor = Mentor(
        name=payload.name,
        expertise=payload.expertise,
        bio=payload.bio,
        materia_id=payload.materia_id,
    )
    db.add(mentor)
    await db.commit()
    await db.refresh(mentor)
    return mentor


@router.get("/mentors", response_model=Page[MentorRead])
async def list_mentors(
    db: DbSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    materia_id: int | None = Query(None),
    sort: str | None = Query(None),
) -> Page[MentorRead]:
    stmt = select(Mentor)
    if materia_id is not None:
        stmt = stmt.where(Mentor.materia_id == materia_id)

    if sort == "name":
        stmt = stmt.order_by(Mentor.name)
    elif sort == "-name":
        stmt = stmt.order_by(Mentor.name.desc())
    elif sort == "id":
        stmt = stmt.order_by(Mentor.id)
    elif sort == "-id":
        stmt = stmt.order_by(Mentor.id.desc())
    elif sort == "expertise":
        stmt = stmt.order_by(Mentor.expertise)
    elif sort == "-expertise":
        stmt = stmt.order_by(Mentor.expertise.desc())
    elif sort is not None:
        raise HTTPException(status_code=422, detail=f"Cannot sort by {sort}")

    count_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = count_result.scalar_one()

    result = await db.execute(stmt.offset(skip).limit(limit))
    items = list(result.scalars().all())

    return Page(items=items, total=total, skip=skip, limit=limit)


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

    if payload.materia_id is not None and await db.get(Materia, payload.materia_id) is None:
        raise HTTPException(status_code=404, detail="Materia not found")

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


@router.get("/mentors/{id}/materias", response_model=list[MateriaNested])
async def listar_materias_do_mentor(id: int, db: DbSession) -> list[Materia]:
    mentor = await db.get(Mentor, id)
    if mentor is None:
        raise HTTPException(status_code=404, detail="Mentor not found")
    if mentor.materia_id is None:
        return []
    materia = await db.get(Materia, mentor.materia_id)
    return [materia]
