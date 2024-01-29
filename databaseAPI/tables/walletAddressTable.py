from sqlalchemy import Column, Integer, String
from databaseAPI.database import Base


class WalletAddress(Base):
    __tablename__ = 'walletAddress'

    Id = Column(Integer, primary_key=True)
    NameNet = Column(String(255), nullable=False)
    Address = Column(String(255), unique=True, nullable=False)
