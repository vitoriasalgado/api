from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.pagination import Page
from app.db.session import get_db
from app.models.aluno import Aluno, aluno_materia
from app.models.materia import Materia


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


class MateriaNested(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class NotaNested(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    materia_id: int
    valor: float


class AlunoDetailRead(AlunoRead):
    materias: list[MateriaNested] = Field(default_factory=list)
    notas: list[NotaNested] = Field(default_factory=list)


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


@router.get("/alunos", response_model=Page[AlunoRead])
async def list_alunos(
    db: DbSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    materia_id: int | None = Query(None),
    sort: str | None = Query(None),
) -> Page[AlunoRead]:
    stmt = select(Aluno)
    if materia_id is not None:
        stmt = stmt.join(aluno_materia).where(aluno_materia.c.materia_id == materia_id)

    if sort == "name":
        stmt = stmt.order_by(Aluno.name)
    elif sort == "-name":
        stmt = stmt.order_by(Aluno.name.desc())
    elif sort == "id":
        stmt = stmt.order_by(Aluno.id)
    elif sort == "-id":
        stmt = stmt.order_by(Aluno.id.desc())
    elif sort is not None:
        raise HTTPException(status_code=422, detail=f"Cannot sort by {sort}")

    count_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = count_result.scalar_one()

    result = await db.execute(stmt.offset(skip).limit(limit))
    items = list(result.scalars().all())

    return Page(items=items, total=total, skip=skip, limit=limit)


@router.get("/alunos/{id}", response_model=AlunoDetailRead)
async def get_aluno(id: int, db: DbSession) -> Aluno:
    stmt = (
        select(Aluno)
        .where(Aluno.id == id)
        .options(selectinload(Aluno.materias), selectinload(Aluno.notas))
    )
    result = await db.execute(stmt)
    aluno = result.scalar_one_or_none()
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
    if await db.get(Aluno, aluno_id) is None:
        raise HTTPException(status_code=404, detail="Aluno not found")
    if await db.get(Materia, materia_id) is None:
        raise HTTPException(status_code=404, detail="Materia not found")

    try:
        await db.execute(aluno_materia.insert().values(aluno_id=aluno_id, materia_id=materia_id))
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Already enrolled") from None


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
