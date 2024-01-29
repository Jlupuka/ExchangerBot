from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from databaseAPI.database import Base
from datetime import datetime


class Submissions(Base):
    __tablename__ = 'submissions'

    Id = Column(Integer, primary_key=True)
    UserId = Column(Integer, ForeignKey('users.Id'), nullable=ForeignKey)
    AddressId = Column(Integer, ForeignKey('walletAddress.Id'), nullable=ForeignKey)
    Amount = Column(Integer, nullable=False)
    TypeTrans = Column(String(255), unique=True, nullable=False)
    AddressUser = Column(String(255), nullable=False)
    DateTime = Column(DateTime, default=datetime.utcnow())
