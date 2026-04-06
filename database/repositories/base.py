"""Base repository with common CRUD operations."""

from typing import Generic, TypeVar, Type, Optional, Sequence
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository providing common database operations."""

    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get a record by primary key."""
        return await self.session.get(self.model, id)

    async def get_all(self) -> Sequence[ModelType]:
        """Get all records."""
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update_by_id(self, id: int, **kwargs) -> Optional[ModelType]:
        """Update a record by ID."""
        instance = await self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await self.session.commit()
            await self.session.refresh(instance)
        return instance

    async def delete_by_id(self, id: int) -> bool:
        """Delete a record by ID."""
        instance = await self.get_by_id(id)
        if instance:
            await self.session.delete(instance)
            await self.session.commit()
            return True
        return False
