from pydantic import BaseModel, Field, validator
from decimal import Decimal
from typing import Optional
from enum import Enum

class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"

class OperationCreate(BaseModel):
    operation_type: OperationType
    amount: Decimal = Field(..., gt=0, decimal_places=8)
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Сумма должна быть положительным числом')
        return v

class WalletCreate(BaseModel):
    wallet_address: str
    balance: Decimal = Field(default=0.0, decimal_places=8)

class WalletResponse(BaseModel):
    wallet_address: str
    balance: Decimal
    
    class Config:
        from_attributes = True