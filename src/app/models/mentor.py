from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Mentor(Base):
    __tablename__ = "mentors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    expertise: Mapped[str] = mapped_column(String(100))
    bio: Mapped[str | None] = mapped_column(Text())
    materia_id: Mapped[int | None] = mapped_column(ForeignKey("materias.id", ondelete="SET NULL"))
