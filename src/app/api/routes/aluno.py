from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.aluno import Aluno, aluno_materia


class AlunoCreate(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr


class AlunoUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    email: EmailStr | None = None


class AlunoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr


DbSession = Annotated[AsyncSession, Depends(get_db)]

router = APIRouter(tags=["alunos"])


@router.post("/alunos", status_code=201, response_model=AlunoRead)
async def create_aluno(payload: AlunoCreate, db: DbSession) -> Aluno:
    aluno = Aluno(name=payload.name, email=payload.email)
    db.add(aluno)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists") from None
    await db.refresh(aluno)
    return aluno


@router.get("/alunos", response_model=list[AlunoRead])
async def list_alunos(db: DbSession) -> list[Aluno]:
    result = await db.execute(select(Aluno))
    return list(result.scalars().all())


@router.get("/alunos/{id}", response_model=AlunoRead)
async def get_aluno(id: int, db: DbSession) -> Aluno:
    aluno = await db.get(Aluno, id)
    if aluno is None:
        raise HTTPException(status_code=404, detail="Aluno not found")
    return aluno


@router.patch("/alunos/{id}", response_model=AlunoRead)
async def update_aluno(id: int, payload: AlunoUpdate, db: DbSession) -> Aluno:
    aluno = await db.get(Aluno, id)
    if aluno is None:
        raise HTTPException(status_code=404, detail="Aluno not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(aluno, key, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists") from None
    await db.refresh(aluno)
    return aluno


@router.delete("/alunos/{id}", status_code=204)
async def delete_aluno(id: int, db: DbSession) -> None:
    aluno = await db.get(Aluno, id)
    if aluno is None:
        raise HTTPException(status_code=404, detail="Aluno not found")
    await db.delete(aluno)
    await db.commit()


@router.post("/alunos/{aluno_id}/materias/{materia_id}", status_code=204)
async def matricular(aluno_id: int, materia_id: int, db: DbSession) -> None:
    aluno = await db.get(Aluno, aluno_id)
    if aluno is None:
        raise HTTPException(status_code=404, detail="Aluno not found") from None

    try:
        await db.execute(aluno_materia.insert().values(aluno_id=aluno_id, materia_id=materia_id))
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409, detail="Already enrolled or materia not found"
            ) from None


@router.delete("/alunos/{aluno_id}/materias/{materia_id}", status_code=204)
async def desmatricular(aluno_id: int, materia_id: int, db: DbSession) -> None:
    result = await db.execute(
        aluno_materia.delete().where(
            (aluno_materia.c.aluno_id == aluno_id) & (aluno_materia.c.materia_id == materia_id)
        )
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    await db.commit()


@router.get("/alunos/{aluno_id}/materias", response_model=list[int])
async def listar_materias_do_aluno(aluno_id: int, db: DbSession) -> list[int]:
    aluno = await db.get(Aluno, aluno_id)
    if aluno is None:
        raise HTTPException(status_code=404, detail="Aluno not found")

    result = await db.execute(
        select(aluno_materia.c.materia_id).where(aluno_materia.c.aluno_id == aluno_id)
    )
    return list(result.scalars().all())
