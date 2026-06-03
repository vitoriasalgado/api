from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.aluno import Aluno
    from app.models.mentor import Mentor
    from app.models.nota import Nota


class Materia(Base):
    __tablename__ = "materias"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    mentores: Mapped[list[Mentor]] = relationship("Mentor", back_populates="materia")
    alunos: Mapped[list[Aluno]] = relationship(secondary="aluno_materia", back_populates="materias")
    notas: Mapped[list[Nota]] = relationship("Nota", back_populates="materia")
