from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.materia import Materia


class MateriaCreate(BaseModel):
    name: str = Field(min_length=1)


class MateriaUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)


class MateriaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class MentorNested(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    expertise: str


class AlunoNested(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr


class MateriaDetailRead(MateriaRead):
    mentores: list[MentorNested] = Field(default_factory=list)
    alunos: list[AlunoNested] = Field(default_factory=list)


DbSession = Annotated[AsyncSession, Depends(get_db)]

router = APIRouter(tags=["materias"])


@router.post("/materias", status_code=201, response_model=MateriaRead)
async def create_materia(payload: MateriaCreate, db: DbSession) -> Materia:
    materia = Materia(name=payload.name)
    db.add(materia)
    await db.commit()
    await db.refresh(materia)
    return materia


@router.get("/materias", response_model=list[MateriaRead])
async def list_materias(db: DbSession) -> list[Materia]:
    result = await db.execute(select(Materia))
    return list(result.scalars().all())


@router.get("/materias/{id}", response_model=MateriaDetailRead)
async def get_materia(id: int, db: DbSession) -> Materia:
    query = (
        select(Materia)
        .where(Materia.id == id)
        .options(selectinload(Materia.mentores), selectinload(Materia.alunos))
    )
    result = await db.execute(query)
    materia = result.scalar_one_or_none()
    if materia is None:
        raise HTTPException(status_code=404, detail="Materia not found")
    return materia


@router.patch("/materias/{id}", response_model=MateriaRead)
async def update_materia(id: int, payload: MateriaUpdate, db: DbSession) -> Materia:
    materia = await db.get(Materia, id)
    if materia is None:
        raise HTTPException(status_code=404, detail="Materia not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(materia, key, value)

    await db.commit()
    await db.refresh(materia)
    return materia


@router.delete("/materias/{id}", status_code=204)
async def delete_materia(id: int, db: DbSession) -> None:
    materia = await db.get(Materia, id)
    if materia is None:
        raise HTTPException(status_code=404, detail="Materia not found")
    await db.delete(materia)
    await db.commit()
