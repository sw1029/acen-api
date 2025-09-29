"""템플릿 및 스케줄 관련 API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ...repositories import ScheduleRepository, TemplateRepository
from ...schemas import (
    ErrorResponse,
    ScheduleCreate,
    ScheduleRead,
    ScheduleUpdate,
    TemplateCreate,
    TemplateRead,
    TemplateUpdate,
)
from ..deps import get_session, require_api_key


error_responses = {
    400: {"model": ErrorResponse, "description": "잘못된 요청"},
    404: {"model": ErrorResponse, "description": "리소스를 찾을 수 없습니다."},
}


router = APIRouter(prefix="/templates", tags=["templates"], responses=error_responses)


@router.get("", response_model=list[TemplateRead])
def list_templates(session: Session = Depends(get_session)) -> list[TemplateRead]:
    repo = TemplateRepository(session)
    return repo.list()


@router.post("", response_model=TemplateRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_api_key)])
def create_template(
    payload: TemplateCreate,
    session: Session = Depends(get_session),
) -> TemplateRead:
    repo = TemplateRepository(session)
    template = repo.create(payload)
    session.commit()
    session.refresh(template)
    return template


@router.get("/{template_id}", response_model=TemplateRead)
def get_template(template_id: int, session: Session = Depends(get_session)) -> TemplateRead:
    repo = TemplateRepository(session)
    template = repo.get(template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return template


@router.patch("/{template_id}", response_model=TemplateRead, dependencies=[Depends(require_api_key)])
def update_template(
    template_id: int,
    payload: TemplateUpdate,
    session: Session = Depends(get_session),
) -> TemplateRead:
    repo = TemplateRepository(session)
    template = repo.get(template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    repo.update(template, payload)
    session.commit()
    session.refresh(template)
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_api_key)])
def delete_template(template_id: int, session: Session = Depends(get_session)) -> Response:
    repo = TemplateRepository(session)
    template = repo.get(template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    repo.delete(template)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{template_id}/schedules",
    response_model=ScheduleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def create_schedule(
    template_id: int,
    payload: ScheduleCreate,
    session: Session = Depends(get_session),
) -> ScheduleRead:
    temp_repo = TemplateRepository(session)
    template = temp_repo.get(template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    repo = ScheduleRepository(session)
    schedule = repo.create(template_id, payload)
    session.commit()
    session.refresh(schedule)
    return schedule


@router.patch(
    "/{template_id}/schedules/{schedule_id}",
    response_model=ScheduleRead,
)
def update_schedule(
    template_id: int,
    schedule_id: int,
    payload: ScheduleUpdate,
    session: Session = Depends(get_session),
) -> ScheduleRead:
    repo = ScheduleRepository(session)
    schedule = repo.get(schedule_id)
    if not schedule or schedule.template_id != template_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")

    repo.update(schedule, payload)
    session.commit()
    session.refresh(schedule)
    return schedule


@router.delete("/{template_id}/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(
    template_id: int,
    schedule_id: int,
    session: Session = Depends(get_session),
) -> Response:
    repo = ScheduleRepository(session)
    schedule = repo.get(schedule_id)
    if not schedule or schedule.template_id != template_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")

    repo.delete(schedule)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
