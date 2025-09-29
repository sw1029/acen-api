"""제품(Product) 관련 API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...repositories import ProductRepository
from ...schemas import ErrorResponse, ProductCreate, ProductRead, ProductUpdate
from ..deps import get_session, require_api_key


error_responses = {
    400: {"model": ErrorResponse, "description": "잘못된 요청"},
    404: {"model": ErrorResponse, "description": "리소스를 찾을 수 없습니다."},
}


router = APIRouter(prefix="/products", tags=["products"], responses=error_responses)


@router.get("", response_model=list[ProductRead])
def list_products(session: Session = Depends(get_session)) -> list[ProductRead]:
    return ProductRepository(session).list()


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_api_key)])
def create_product(payload: ProductCreate, session: Session = Depends(get_session)) -> ProductRead:
    repo = ProductRepository(session)
    product = repo.create(payload)
    session.commit()
    session.refresh(product)
    return product
