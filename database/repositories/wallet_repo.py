"""Wallet repository for multi-account management."""

from typing import Optional, Sequence
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.wallet import Wallet
from database.repositories.base import BaseRepository


class WalletRepository(BaseRepository[Wallet]):
    """Repository for Wallet model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Wallet)

    async def get_user_wallets(self, user_id: int) -> Sequence[Wallet]:
        """Get all wallets for a user."""
        result = await self.session.execute(
            select(Wallet).where(Wallet.user_id == user_id)
        )
        return result.scalars().all()

    async def get_default_wallet(self, user_id: int) -> Optional[Wallet]:
        """Get default wallet for a user."""
        result = await self.session.execute(
            select(Wallet).where(
                and_(Wallet.user_id == user_id, Wallet.is_default == True)
            )
        )
        return result.scalar_one_or_none()

    async def create_default_wallet(self, user_id: int) -> Wallet:
        """Create a default cash wallet for a new user."""
        return await self.create(
            user_id=user_id,
            name="Naqd pul",
            type="cash",
            icon="💵",
            balance=0.0,
            is_default=True,
        )

    async def update_balance(
        self, wallet_id: int, amount: float, is_expense: bool = True
    ) -> Optional[Wallet]:
        """Update wallet balance after a transaction."""
        wallet = await self.get_by_id(wallet_id)
        if wallet:
            if is_expense:
                wallet.balance -= amount
            else:
                wallet.balance += amount
            await self.session.commit()
            await self.session.refresh(wallet)
        return wallet

    async def transfer(
        self, from_wallet_id: int, to_wallet_id: int, amount: float
    ) -> bool:
        """Transfer money between wallets."""
        from_wallet = await self.get_by_id(from_wallet_id)
        to_wallet = await self.get_by_id(to_wallet_id)
        if from_wallet and to_wallet:
            from_wallet.balance -= amount
            to_wallet.balance += amount
            await self.session.commit()
            return True
        return False
