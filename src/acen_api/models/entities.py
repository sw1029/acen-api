"""SQLAlchemy ORM으로 정의한 도메인 모델."""

from __future__ import annotations

from datetime import date as date_type, datetime

from sqlalchemy import Date as SADate
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class User(TimestampMixin, Base):
    """서비스를 이용하는 사용자."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True)
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    calendars: Mapped[list["Calendar"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    dates: Mapped[list["Date"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )


class ApiKey(TimestampMixin, Base):
    """API 호출 보호용 키."""

    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Template(TimestampMixin, Base):
    """스케줄 템플릿을 정의."""

    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    theme: Mapped[str | None] = mapped_column(String(50), nullable=True)

    schedules: Mapped[list["Schedule"]] = relationship(
        back_populates="template", cascade="all, delete-orphan", passive_deletes=True
    )
    dates: Mapped[list["Date"]] = relationship(back_populates="template")


class Schedule(TimestampMixin, Base):
    """템플릿에 속한 개별 스케줄 항목."""

    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    template_id: Mapped[int] = mapped_column(
        ForeignKey("templates.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tags: Mapped[str | None] = mapped_column(String(120), nullable=True)
    extra_info: Mapped[str | None] = mapped_column(Text, nullable=True)

    template: Mapped[Template] = relationship(back_populates="schedules")


class Calendar(TimestampMixin, Base):
    """사용자 일자 로그를 모으는 캘린더."""

    __tablename__ = "calendars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    dates: Mapped[list["Date"]] = relationship(
        back_populates="calendar", cascade="all, delete-orphan", passive_deletes=True
    )
    user: Mapped[User] = relationship(back_populates="calendars")


class Date(TimestampMixin, Base):
    """스케줄 수행 및 모델 결과를 기록하는 일자 로그."""

    __tablename__ = "dates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    calendar_id: Mapped[int] = mapped_column(
        ForeignKey("calendars.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    template_id: Mapped[int | None] = mapped_column(
        ForeignKey("templates.id", ondelete="SET NULL"), nullable=True
    )
    scheduled_date: Mapped[date_type] = mapped_column(SADate, nullable=False)
    completion_ratio: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    schedule_done: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    schedule_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)

    calendar: Mapped[Calendar] = relationship(back_populates="dates")
    template: Mapped[Template | None] = relationship(back_populates="dates")
    user: Mapped[User] = relationship(back_populates="dates")
    model_results: Mapped[list["ModelResult"]] = relationship(
        back_populates="date", cascade="all, delete-orphan", passive_deletes=True
    )
    feedback_entries: Mapped[list["Feedback"]] = relationship(
        back_populates="date", cascade="all, delete-orphan", passive_deletes=True
    )


class ModelResult(TimestampMixin, Base):
    """일자 로그에 연결된 모델 추론 결과."""

    __tablename__ = "model_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date_id: Mapped[int] = mapped_column(
        ForeignKey("dates.id", ondelete="CASCADE"), nullable=False
    )
    result_type: Mapped[str] = mapped_column(String(32), nullable=False)
    label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    data: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)

    date: Mapped[Date] = relationship(back_populates="model_results")


class Feedback(TimestampMixin, Base):
    """평가지표를 요약한 피드백."""

    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date_id: Mapped[int] = mapped_column(
        ForeignKey("dates.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    severity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    advice: Mapped[str | None] = mapped_column(Text, nullable=True)

    date: Mapped[Date] = relationship(back_populates="feedback_entries")
    suggestions: Mapped[list["Suggest"]] = relationship(
        back_populates="feedback", cascade="all, delete-orphan", passive_deletes=True
    )


class Product(TimestampMixin, Base):
    """시스템이 추천하는 스킨케어 제품."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(80), nullable=True)
    tags: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    suggestions: Mapped[list["Suggest"]] = relationship(back_populates="product")


class Suggest(TimestampMixin, Base):
    """피드백과 제품을 연결하는 추천 레코드."""

    __tablename__ = "suggestions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    feedback_id: Mapped[int] = mapped_column(
        ForeignKey("feedback.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)

    feedback: Mapped[Feedback] = relationship(back_populates="suggestions")
    product: Mapped[Product] = relationship(back_populates="suggestions")
