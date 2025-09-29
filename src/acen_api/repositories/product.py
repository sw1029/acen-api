"""제품 및 추천 리포지토리."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Product
from ..schemas import ProductCreate, ProductUpdate
from .base import BaseRepository


class ProductRepository(BaseRepository):
    """제품 CRUD 및 태그 기반 검색."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def list(self) -> list[Product]:
        stmt = select(Product).order_by(Product.id)
        return list(self.session.execute(stmt).scalars())

    def search_by_tag(self, tag: str) -> list[Product]:
        like_pattern = f"%{tag}%"
        stmt = select(Product).where(Product.tags.ilike(like_pattern)).order_by(Product.id)
        return list(self.session.execute(stmt).scalars())

    def get(self, product_id: int) -> Product | None:
        stmt = select(Product).where(Product.id == product_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create(self, data: ProductCreate | dict[str, Any]) -> Product:
        payload = self._to_dict(data, exclude_none=True)
        product = Product(**payload)
        self.session.add(product)
        self.session.flush()
        return product

    def update(self, product: Product, data: ProductUpdate | dict[str, Any]) -> Product:
        payload = self._to_dict(data, exclude_none=True)
        self._apply(product, payload)
        self.session.flush()
        return product

    def delete(self, product: Product) -> None:
        self.session.delete(product)
