from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class Nota(Base):
    __tablename__ = "notas"

    id: Mapped[int] = mapped_column(primary_key=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("alunos.id", ondelete="CASCADE"))
    materia_id: Mapped[int] = mapped_column(ForeignKey("materias.id", ondelete="CASCADE")) 
    valor: Mapped[float] = mapped_column(Float)