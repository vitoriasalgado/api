from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.pagination import Page
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.db.session import get_db
from app.models.aluno import Aluno
from app.models.materia import Materia
from app.models.nota import Nota


class NotaCreate(BaseModel):
    aluno_id: int
    materia_id: int
    valor: float = Field(ge=0, le=10)


class NotaUpdate(BaseModel):
    valor: float = Field(ge=0, le=10)


class NotaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    aluno_id: int
    materia_id: int
    valor: float


DbSession = Annotated[AsyncSession, Depends(get_db)]

router = APIRouter(tags=["notas"])


@router.post("/notas", status_code=201, response_model=NotaRead)
async def create_nota(payload: NotaCreate, db: DbSession) -> Nota:
    if await db.get(Aluno, payload.aluno_id) is None:
        raise NotFoundError("Aluno not found", {"id": payload.aluno_id})
    if await db.get(Materia, payload.materia_id) is None:
        raise NotFoundError("Materia not found", {"id": payload.materia_id})

    nota = Nota(aluno_id=payload.aluno_id, materia_id=payload.materia_id, valor=payload.valor)
    db.add(nota)
    await db.commit()
    await db.refresh(nota)
    return nota


@router.get("/notas", response_model=Page[NotaRead])
async def list_notas(
    db: DbSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    aluno_id: int | None = Query(None),
    materia_id: int | None = Query(None),
    sort: str | None = Query(None),
) -> Page[NotaRead]:
    stmt = select(Nota)
    if aluno_id is not None:
        stmt = stmt.where(Nota.aluno_id == aluno_id)
    if materia_id is not None:
        stmt = stmt.where(Nota.materia_id == materia_id)

    if sort == "id":
        stmt = stmt.order_by(Nota.id)
    elif sort == "-id":
        stmt = stmt.order_by(Nota.id.desc())
    elif sort == "valor":
        stmt = stmt.order_by(Nota.valor)
    elif sort == "-valor":
        stmt = stmt.order_by(Nota.valor.desc())
    elif sort is not None:
        raise BusinessRuleError(f"Cannot sort by {sort}", {"field": "sort", "value": sort})

    count_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = count_result.scalar_one()

    result = await db.execute(stmt.offset(skip).limit(limit))
    items = list(result.scalars().all())

    return Page(items=items, total=total, skip=skip, limit=limit)


@router.get("/notas/{id}", response_model=NotaRead)
async def get_nota(id: int, db: DbSession) -> Nota:
    nota = await db.get(Nota, id)
    if nota is None:
        raise NotFoundError("Nota not found", {"id": id})
    return nota


@router.patch("/notas/{id}", response_model=NotaRead)
async def update_nota(id: int, payload: NotaUpdate, db: DbSession) -> Nota:
    nota = await db.get(Nota, id)
    if nota is None:
        raise NotFoundError("Nota not found", {"id": id})

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(nota, key, value)

    await db.commit()
    await db.refresh(nota)
    return nota


@router.delete("/notas/{id}", status_code=204)
async def delete_nota(id: int, db: DbSession) -> None:
    nota = await db.get(Nota, id)
    if nota is None:
        raise NotFoundError("Nota not found", {"id": id})
    await db.delete(nota)
    await db.commit()
