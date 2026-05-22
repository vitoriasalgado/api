from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.aluno import Aluno

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
        raise HTTPException(status_code=409, detail="Email already exists")
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
        raise HTTPException(status_code=409, detail="Email already exists")
    await db.refresh(aluno)
    return aluno

@router.delete("/alunos/{id}", status_code=204)
async def delete_aluno(id: int, db: DbSession) -> None:
    aluno = await db.get(Aluno, id)
    if aluno is None:
        raise HTTPException(status_code=404, detail="Aluno not found")
    await db.delete(aluno)
    await db.commit()