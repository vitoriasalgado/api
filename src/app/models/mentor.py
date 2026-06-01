from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.materia import Materia


class Mentor(Base):
    __tablename__ = "mentors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    expertise: Mapped[str] = mapped_column(String(100))
    bio: Mapped[str | None] = mapped_column(Text())
    materia_id: Mapped[int | None] = mapped_column(ForeignKey("materias.id", ondelete="SET NULL"))
    materia: Mapped[Materia | None] = relationship(back_populates="mentores")
