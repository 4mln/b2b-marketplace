from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class WalletBase(BaseModel):
    currency: str
    currency_type: str = "fiat"  # fiat or crypto

class WalletCreate(WalletBase):
    user_id: int

class WalletUpdate(BaseModel):
    is_active: Optional[bool] = None

class WalletOut(WalletBase):
    id: int
    user_id: int
    balance: float
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    amount: float
    transaction_type: str  # deposit, withdrawal, transfer, cashback, fee
    reference: Optional[str] = None
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    wallet_id: int

class TransactionUpdate(BaseModel):
    status: Optional[str] = None

class TransactionOut(TransactionBase):
    id: int
    wallet_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DepositRequest(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str

class WithdrawalRequest(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str

class TransferRequest(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str
    recipient_id: int

class WalletBalance(BaseModel):
    currency: str
    balance: float
    currency_type: str

class UserWallets(BaseModel):
    user_id: int
    wallets: List[WalletBalance]