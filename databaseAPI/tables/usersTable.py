import datetime
from sqlalchemy import Column, Integer, BigInteger, Boolean, DateTime
from databaseAPI.database import Base


class Users(Base):
    __tablename__ = 'users'

    Id = Column(Integer, primary_key=True)
    UserId = Column(BigInteger, unique=True, nullable=False)
    Admin = Column(Boolean, default=False)
    WorkType = Column(Boolean, default=False)
    KYC = Column(Boolean, default=False)
    DateTime = Column(DateTime, default=datetime.datetime.utcnow)
