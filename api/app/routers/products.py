"""Product catalog endpoints (Epic 2, Story 2.1)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user, require_manager
from app.models import Product, User
from app.schemas.common import Page
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])

_NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")


@router.get("", response_model=Page[ProductOut])
async def list_products(
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
    q: str | None = Query(default=None, description="Search by product name"),
    include_inactive: bool = Query(default=False),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> Page[ProductOut]:
    filters = []
    if not include_inactive:
        filters.append(Product.is_active.is_(True))
    if q:
        filters.append(Product.name.ilike(f"%{q}%"))

    total = await db.scalar(select(func.count()).select_from(Product).where(*filters))
    rows = (
        await db.scalars(
            select(Product).where(*filters).order_by(Product.name).limit(limit).offset(offset)
        )
    ).all()
    return Page(
        items=[ProductOut.model_validate(p) for p in rows],
        total=total or 0,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    body: ProductCreate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_manager),
) -> ProductOut:
    product = Product(**body.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return ProductOut.model_validate(product)


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> ProductOut:
    product = await db.get(Product, product_id)
    if product is None:
        raise _NOT_FOUND
    return ProductOut.model_validate(product)


@router.patch("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: uuid.UUID,
    body: ProductUpdate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_manager),
) -> ProductOut:
    product = await db.get(Product, product_id)
    if product is None:
        raise _NOT_FOUND
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    await db.commit()
    await db.refresh(product)
    return ProductOut.model_validate(product)


@router.delete("/{product_id}", response_model=ProductOut)
async def deactivate_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_manager),
) -> ProductOut:
    """Soft-delete: flip is_active off so historical samples/orders keep the product."""
    product = await db.get(Product, product_id)
    if product is None:
        raise _NOT_FOUND
    product.is_active = False
    await db.commit()
    await db.refresh(product)
    return ProductOut.model_validate(product)
