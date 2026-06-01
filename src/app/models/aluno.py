from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.materia import Materia
    from app.models.nota import Nota

aluno_materia = Table(
    "aluno_materia",
    Base.metadata,
    Column("aluno_id", ForeignKey("alunos.id", ondelete="CASCADE"), primary_key=True),
    Column("materia_id", ForeignKey("materias.id", ondelete="CASCADE"), primary_key=True),
)


class Aluno(Base):
    __tablename__ = "alunos"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    materias: Mapped[list[Materia]] = relationship(
        secondary="aluno_materia", back_populates="alunos"
    )
    notas: Mapped[list[Nota]] = relationship(back_populates="aluno")
