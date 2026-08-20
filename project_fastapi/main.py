from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from .src import models, schemas
from .src.db_conn import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Управление кошельками", version="1.0.0")

@app.get("/")
async def read_root():
    return {"message": "API для управления кошельками", "docs": "/docs"}

@app.post("/api/v1/wallets/{wallet_uuid}/operation")
async def create_operation(
    wallet_uuid: str,
    operation: schemas.OperationCreate,
    db: Session = Depends(get_db)
):
    wallet = db.query(models.Wallet).filter(
        models.Wallet.wallet_address == wallet_uuid
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кошелек не найден"
        )
    
    if operation.operation_type == schemas.OperationType.DEPOSIT:
        wallet.balance += operation.amount
        operation_name = "Пополнение"
    elif operation.operation_type == schemas.OperationType.WITHDRAW:
        if wallet.balance < operation.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Недостаточно средств. Доступно: {wallet.balance}, запрошено: {operation.amount}"
            )
        wallet.balance -= operation.amount
        operation_name = "Снятие"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный тип операции. Используйте DEPOSIT или WITHDRAW"
        )
    
    # Сохраняем изменения
    db.commit()
    db.refresh(wallet)
    
    return {
        "wallet_uuid": wallet_uuid,
        "operation_type": operation.operation_type.value,
        "operation_name": operation_name,
        "amount": operation.amount,
        "new_balance": wallet.balance,
        "status": "completed"
    }


@app.get("/api/v1/wallets/{wallet_uuid}")
async def get_wallet(
    wallet_uuid: str,
    db: Session = Depends(get_db)
):
    wallet = db.query(models.Wallet).filter(
        models.Wallet.wallet_address == wallet_uuid
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кошелек не найден"
        )
    
    return {
        "wallet_uuid": wallet.wallet_address,
        "balance": wallet.balance
    }

@app.post("/api/v1/wallets/", status_code=status.HTTP_201_CREATED)
async def create_wallet(
    wallet: schemas.WalletCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(models.Wallet).filter(
        models.Wallet.wallet_address == wallet.wallet_address
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Кошелек с таким адресом уже существует"
        )
    
    db_wallet = models.Wallet(
        wallet_address=wallet.wallet_address,
        balance=wallet.balance
    )
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    
    return {
        "wallet_uuid": db_wallet.wallet_address,
        "balance": db_wallet.balance,
        "status": "created"
    }