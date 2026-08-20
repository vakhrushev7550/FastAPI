from sqlalchemy import Column, Integer, String, Numeric
from .db_conn import Base

class Wallet(Base):
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String, unique=True, index=True, nullable=False)
    balance = Column(Numeric(precision=18, scale=8), nullable=False, default=0.0)