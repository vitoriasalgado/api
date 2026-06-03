from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.aluno import Aluno
    from app.models.materia import Materia


class Nota(Base):
    __tablename__ = "notas"

    id: Mapped[int] = mapped_column(primary_key=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("alunos.id", ondelete="CASCADE"))
    materia_id: Mapped[int] = mapped_column(ForeignKey("materias.id", ondelete="CASCADE"))
    valor: Mapped[float] = mapped_column(Float)

    aluno: Mapped[Aluno] = relationship(back_populates="notas")
    materia: Mapped[Materia] = relationship(back_populates="notas")
