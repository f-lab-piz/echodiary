from __future__ import annotations

import enum
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ImageStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class EntryStatus(str, enum.Enum):
    DRAFT = "draft"
    SAVED = "saved"


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class Persona(Base):
    __tablename__ = "personas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    account_id: Mapped[str] = mapped_column(String(36), index=True)
    name: Mapped[str] = mapped_column(String(100))
    tone: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_status: Mapped[ImageStatus] = mapped_column(Enum(ImageStatus), default=ImageStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    diary_links: Mapped[list[DiaryPersona]] = relationship(back_populates="persona", cascade="all, delete-orphan")


class Diary(Base):
    __tablename__ = "diaries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    account_id: Mapped[str] = mapped_column(String(36), index=True)
    title: Mapped[str] = mapped_column(String(120))
    default_persona_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("personas.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    persona_links: Mapped[list[DiaryPersona]] = relationship(back_populates="diary", cascade="all, delete-orphan")
    entries: Mapped[list[Entry]] = relationship(back_populates="diary", cascade="all, delete-orphan")


class DiaryPersona(Base):
    __tablename__ = "diary_personas"
    __table_args__ = (UniqueConstraint("diary_id", "persona_id", name="uq_diary_persona"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    diary_id: Mapped[str] = mapped_column(String(36), ForeignKey("diaries.id", ondelete="CASCADE"), index=True)
    persona_id: Mapped[str] = mapped_column(String(36), ForeignKey("personas.id", ondelete="CASCADE"), index=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    diary: Mapped[Diary] = relationship(back_populates="persona_links")
    persona: Mapped[Persona] = relationship(back_populates="diary_links")


class Entry(Base):
    __tablename__ = "entries"
    __table_args__ = (
        CheckConstraint("input_keywords IS NOT NULL OR input_text IS NOT NULL", name="ck_entry_input_required"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    diary_id: Mapped[str] = mapped_column(String(36), ForeignKey("diaries.id", ondelete="CASCADE"), index=True)
    persona_id: Mapped[str] = mapped_column(String(36), ForeignKey("personas.id"), index=True)
    input_keywords: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    draft: Mapped[str] = mapped_column(Text)
    status: Mapped[EntryStatus] = mapped_column(Enum(EntryStatus), default=EntryStatus.DRAFT)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    diary: Mapped[Diary] = relationship(back_populates="entries")
