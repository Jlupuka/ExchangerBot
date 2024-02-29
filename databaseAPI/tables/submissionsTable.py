from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from databaseAPI.database import Base
from datetime import datetime


class Submissions(Base):
    __tablename__ = 'submissions'

    Id = Column(Integer, primary_key=True)
    UserId = Column(Integer, ForeignKey('users.Id'), nullable=ForeignKey)
    AddressId = Column(Integer, ForeignKey('walletaddress.Id'), nullable=ForeignKey)
    AmountTo = Column(Float, nullable=False)
    AmountFrom = Column(Float, nullable=False)
    TypeTrans = Column(String(255), nullable=False)  # crypto-rub | rub-crypto | crypto-crypto
    AddressUser = Column(String(255), nullable=False)
    Status = Column(String(255), default='WAIT')  # WAIT | ACCEPTED | COMPLETED
    AdminId = Column(Integer, default=None)
    DateTime = Column(DateTime, default=datetime.utcnow())
