from sqlalchemy import Column, Integer, String, Float, Boolean
from databaseAPI.database import Base


class WalletAddress(Base):
    __tablename__ = 'walletaddress'

    Id = Column(Integer, primary_key=True)
    NameNet = Column(String(255), nullable=False)
    Address = Column(String(255), unique=True, nullable=False)
    Status = Column(Boolean, default=True)  # True | False
    Percent = Column(Float, default=5.0)
    typeWallet = Column(String(20), nullable=False)  # Fiat | Crypto
