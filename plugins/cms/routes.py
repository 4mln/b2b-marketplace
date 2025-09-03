from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.db import get_session
from .models import Page


router = APIRouter()


@router.get("/pages/{slug}")
async def get_page(slug: str, db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    result = await db.execute(select(Page).where(Page.slug == slug))
    page = result.scalars().first()
    if not page:
        raise HTTPException(status_code=404, detail="Not found")
    return page


@router.post("/pages")
async def create_page(slug: str, title: str, content: str, db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    page = Page(slug=slug, title=title, content=content)
    db.add(page)
    await db.commit()
    await db.refresh(page)
    return page


@router.patch("/pages/{slug}")
async def update_page(slug: str, title: str | None = None, content: str | None = None, db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    result = await db.execute(select(Page).where(Page.slug == slug))
    page = result.scalars().first()
    if not page:
        raise HTTPException(status_code=404, detail="Not found")
    if title is not None:
        page.title = title
    if content is not None:
        page.content = content
    await db.commit()
    await db.refresh(page)
    return page







