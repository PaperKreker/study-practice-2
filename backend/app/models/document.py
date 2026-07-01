import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Document(Base):
    """ORM-модель загруженного документа.

    Хранит метаданные файла (имя, размер, количество чанков) и связь
    с пользователем-владельцем, а также с записями истории поиска,
    ссылающимися на этот документ. Сам текст документа хранится не здесь,
    а в виде чанков в Elasticsearch.
    """

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    size_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    chunk_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    user: Mapped["User | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User",
        back_populates="documents",
    )
    search_history: Mapped[list["SearchHistory"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "SearchHistory",
        back_populates="document",
    )

    def __repr__(self) -> str:
        """Возвращает краткое строковое представление документа для отладки."""
        return f"<Document id={self.id} file_name={self.file_name!r}>"
