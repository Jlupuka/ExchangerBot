import enum
import datetime
from typing import Annotated, List, Optional

from sqlalchemy import ForeignKey, text, BigInteger, event
from sqlalchemy.orm import mapped_column, Mapped, relationship

from databaseAPI.database import Base

INTPKA = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
CREATED_AT = Annotated[
    datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))
]
UPDATE_AT = Annotated[
    datetime.datetime,
    mapped_column(
        server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.utcnow
    ),
]
BOOLF = Annotated[bool, mapped_column(default=False)]


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

    Id: Mapped[INTPKA]
    UserId: Mapped[int] = mapped_column(ForeignKey("users.Id"), nullable=False)
    WalletId: Mapped[int] = mapped_column(ForeignKey("wallets.Id"), nullable=False)
    AmountTo: Mapped[float]
    AmountFrom: Mapped[float]
    CurrencyTo: Mapped[str]
    TypeTrans: Mapped[TypesTrans]
    AddressUser: Mapped[str]
    Status: Mapped[Statuses] = mapped_column(default=Statuses.wait)
    AdminId: Mapped[Optional[int]] = mapped_column(ForeignKey("users.Id"), default=None)
    created_at: Mapped[CREATED_AT]
    update_at: Mapped[UPDATE_AT]

    wallet: Mapped["Wallets"] = relationship(
        foreign_keys=[WalletId],
        primaryjoin="Submissions.WalletId == Wallets.Id",
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

    Id: Mapped[INTPKA]
    UserId: Mapped[int] = mapped_column(BigInteger, unique=True)
    IsAdmin: Mapped[BOOLF]
    StatusWork: Mapped[BOOLF]
    KYC: Mapped[BOOLF]
    created_at: Mapped[CREATED_AT]

    admin_submissions: Mapped[Optional[List["Submissions"]]] = relationship(
        back_populates="admin", foreign_keys=[Submissions.AdminId]
    )
    user_submissions: Mapped[Optional[List["Submissions"]]] = relationship(
        back_populates="user", foreign_keys=[Submissions.UserId]
    )


class Wallets(Base):
    __tablename__ = "wallets"

    Id: Mapped[INTPKA]
    NameNet: Mapped[str]
    Address: Mapped[str] = mapped_column(unique=True, nullable=False)
    Status: Mapped[bool] = mapped_column(default=True)
    Percent: Mapped[float] = mapped_column(default=1.05)
    typeWallet: Mapped[TypesWallet]
    MnemonicId: Mapped[Optional[int]] = mapped_column(
        ForeignKey("mnemonic.Id", ondelete="CASCADE")
    )

    mnemonic: Mapped[Optional["MnemonicWallets"]] = relationship(
        back_populates="wallet", foreign_keys=[MnemonicId], cascade="all, delete"
    )


class MnemonicWallets(Base):
    __tablename__ = "mnemonic"

    Id: Mapped[INTPKA]
    WalletId: Mapped[int] = mapped_column(
        ForeignKey("wallets.Id", ondelete="CASCADE"), unique=True
    )
    EncryptMnemonic: Mapped[str]

    wallet: Mapped["Wallets"] = relationship(
        foreign_keys=[WalletId], cascade="all, delete"
    )


@event.listens_for(MnemonicWallets, "after_insert")
def receive_after_insert(mapper, connection, target: MnemonicWallets):
    wallet_id = target.WalletId
    mnemonic_id = target.Id

    connection.execute(
        Wallets.__table__.update()
        .where(Wallets.Id == wallet_id)
        .values(MnemonicId=mnemonic_id)
    )
