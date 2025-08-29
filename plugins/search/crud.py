from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from plugins.search.models import SavedSearch, SearchEvent
from plugins.search.schemas import SavedSearchCreate


async def create_saved_search(db: AsyncSession, user_id: int, data: SavedSearchCreate) -> SavedSearch:
    s = SavedSearch(user_id=user_id, query=data.query)
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return s


async def list_saved_searches(db: AsyncSession, user_id: int) -> list[SavedSearch]:
    result = await db.execute(select(SavedSearch).where(SavedSearch.user_id == user_id))
    return result.scalars().all()


async def log_search(db: AsyncSession, query: str) -> None:
    db.add(SearchEvent(query=query))
    await db.commit()


