import enum
import datetime
from typing import Annotated, List, Optional

from sqlalchemy import ForeignKey, text, BigInteger
from sqlalchemy.orm import mapped_column, Mapped, relationship

from databaseAPI.database import Base

intpka = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
created_at = Annotated[
    datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))
]
update_at = Annotated[
    datetime.datetime,
    mapped_column(
        server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.utcnow
    ),
]
boolf = Annotated[bool, mapped_column(default=False)]


class Statuses(enum.Enum):
    wait = "WAIT"
    accepted = "ACCEPTED"
    completed = "COMPLETED"


class TypesTrans(enum.Enum):
    crypto_rub = "CRYPTO/RUB"
    rub_crypto = "RUB/CRYPTO"
    crypto_crypto = "CRYPTO/CRYPTO"


class TypesWallet(enum.Enum):
    rub = "RUB"
    crypto = "CRYPTO"


class Submissions(Base):
    __tablename__ = "submissions"

    Id: Mapped[intpka]
    UserId: Mapped[int] = mapped_column(ForeignKey("users.Id"), nullable=False)
    AddressId: Mapped[int] = mapped_column(ForeignKey("wallets.Id"), nullable=False)
    AmountTo: Mapped[float]
    AmountFrom: Mapped[float]
    CurrencyTo: Mapped[str]
    TypeTrans: Mapped[TypesTrans]
    AddressUser: Mapped[str]
    Status: Mapped[Statuses] = mapped_column(default=Statuses.wait)
    AdminId: Mapped[Optional[int]] = mapped_column(ForeignKey("users.Id"), default=None)
    created_at: Mapped[created_at]
    update_at: Mapped[update_at]

    wallet: Mapped["Wallets"] = relationship(
        foreign_keys=[AddressId],
        primaryjoin="Submissions.AddressId == Wallets.Id",
    )

    user: Mapped["Users"] = relationship(
        back_populates="user_submissions",
        foreign_keys=[UserId],
        primaryjoin="Submissions.UserId == Users.Id",
    )

    admin: Mapped["Users"] = relationship(
        back_populates="admin_submissions",
        foreign_keys=[AdminId],
        primaryjoin="Submissions.AdminId == Users.Id",
    )


class Users(Base):
    __tablename__ = "users"

    Id: Mapped[intpka]
    UserId: Mapped[int] = mapped_column(BigInteger, unique=True)
    Admin: Mapped[boolf]
    WorkType: Mapped[boolf]
    KYC: Mapped[boolf]
    created_at: Mapped[created_at]

    admin_submissions: Mapped[Optional[List["Submissions"]]] = relationship(
        back_populates="admin", foreign_keys=[Submissions.AdminId]
    )
    user_submissions: Mapped[Optional[List["Submissions"]]] = relationship(
        back_populates="user", foreign_keys=[Submissions.UserId]
    )


class Wallets(Base):
    __tablename__ = "wallets"

    Id: Mapped[intpka]
    NameNet: Mapped[str]
    Address: Mapped[str] = mapped_column(unique=True, nullable=False)
    Status: Mapped[bool] = mapped_column(default=True)
    Percent: Mapped[float] = mapped_column(default=1.05)
    typeWallet: Mapped[TypesWallet]
