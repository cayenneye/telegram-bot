from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from models.transaction_sources import TransactionSource
from models.users import UserPartial

__all__ = ('Deposit',)


class Deposit(BaseModel):
    id: UUID
    user: UserPartial
    amount: int
    description: str
    source: TransactionSource
    created_at: datetime

    class Config:
        use_enum_values = True
