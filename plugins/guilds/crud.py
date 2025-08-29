from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import Guild
from .schemas import GuildCreate, GuildUpdate


async def create_guild(db: AsyncSession, data: GuildCreate) -> Guild:
    guild = Guild(**data.dict())
    db.add(guild)
    await db.commit()
    await db.refresh(guild)
    return guild


async def get_guild_by_slug(db: AsyncSession, slug: str) -> Guild | None:
    result = await db.execute(select(Guild).where(Guild.slug == slug))
    return result.scalars().first()


async def get_guild(db: AsyncSession, guild_id: int) -> Guild | None:
    return await db.get(Guild, guild_id)


async def list_guilds(db: AsyncSession) -> list[Guild]:
    result = await db.execute(select(Guild))
    return result.scalars().all()


async def update_guild(db: AsyncSession, guild_id: int, data: GuildUpdate) -> Guild | None:
    guild = await db.get(Guild, guild_id)
    if not guild:
        return None
    for k, v in data.dict(exclude_unset=True).items():
        setattr(guild, k, v)
    await db.commit()
    await db.refresh(guild)
    return guild


async def delete_guild(db: AsyncSession, guild_id: int) -> bool:
    guild = await db.get(Guild, guild_id)
    if not guild:
        return False
    await db.delete(guild)
    await db.commit()
    return True


