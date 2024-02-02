from sqlalchemy import Column, Integer, String, Float
from databaseAPI.database import Base


class WalletAddress(Base):
    __tablename__ = 'walletaddress'

    Id = Column(Integer, primary_key=True)
    NameNet = Column(String(255), nullable=False)
    Address = Column(String(255), unique=True, nullable=False)
    Percent = Column(Float, default=5.0)
