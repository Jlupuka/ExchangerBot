from dataclasses import dataclass
from environs import Env


@dataclass
class TokenBot:
    TOKEN: str


@dataclass
class PostgreSQL:
    USER: str
    PASSWORD: str
    HOST: str
    PORT: int
    NAME: str


@dataclass
class RedisStorge:
    HOST: str
    PORT: int


@dataclass
class Admins:
    ADMINID: list


@dataclass
class Config:
    TelegramBot: TokenBot
    DataBase: PostgreSQL
    Redis: RedisStorge
    AdminId: Admins


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path=path)
    return Config(
        TelegramBot=TokenBot(
            TOKEN=env('BOT-TOKEN')
        ),
        DataBase=PostgreSQL(
            USER=env('DB-USER'),
            PASSWORD=env('DB-PASSWORD'),
            HOST=env('DB-HOST'),
            PORT=env('DB-PORT'),
            NAME=env('DB-NAME')
        ),
        Redis=RedisStorge(
            HOST=env('REDIS-HOST'),
            PORT=env('REDIS-PORT')
        ),
        AdminId=Admins(
            ADMINID=list(int(adm_id)
                         for adm_id in map(
                lambda admins: admins.strip(),
                env('ADMIN-ID').split(','))
                         if adm_id)
        )
    )
