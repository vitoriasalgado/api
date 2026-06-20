from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
        raise HTTPException(status_code=404, detail="Aluno not found")
    if await db.get(Materia, payload.materia_id) is None:
        raise HTTPException(status_code=404, detail="Materia not found")

    nota = Nota(aluno_id=payload.aluno_id, materia_id=payload.materia_id, valor=payload.valor)
    db.add(nota)
    await db.commit()
    await db.refresh(nota)
    return nota


@router.get("/notas", response_model=list[NotaRead])
async def list_notas(db: DbSession) -> list[Nota]:
    result = await db.execute(select(Nota))
    return list(result.scalars().all())


@router.get("/notas/{id}", response_model=NotaRead)
async def get_nota(id: int, db: DbSession) -> Nota:
    nota = await db.get(Nota, id)
    if nota is None:
        raise HTTPException(status_code=404, detail="Nota not found")
    return nota


@router.patch("/notas/{id}", response_model=NotaRead)
async def update_nota(id: int, payload: NotaUpdate, db: DbSession) -> Nota:
    nota = await db.get(Nota, id)
    if nota is None:
        raise HTTPException(status_code=404, detail="Nota not found")

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
        raise HTTPException(status_code=404, detail="Nota not found")
    await db.delete(nota)
    await db.commit()
