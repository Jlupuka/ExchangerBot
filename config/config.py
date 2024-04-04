from dataclasses import dataclass
from typing import Union

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
class SecretKey:
    SECRETKEY: bytes


@dataclass
class TronGridAPI:
    APIKEY: str


@dataclass
class Config:
    TelegramBot: TokenBot
    DataBase: PostgreSQL
    Redis: RedisStorge
    AdminId: Admins
    SecretKey: SecretKey
    TronGridAPI: TronGridAPI


def load_config(path: Union[str, None] = None) -> Config:
    """
    Loads all data from env and returns it as a dataclass
    :param path: (Union[str, None]) the path where the env is stored
    :return: (Config)
    """
    env = Env()
    env.read_env(path=path)
    return Config(
        TelegramBot=TokenBot(TOKEN=env("BOT-TOKEN")),
        DataBase=PostgreSQL(
            USER=env("POSTGRES_USER"),
            PASSWORD=env("POSTGRES_PASSWORD"),
            HOST=env("POSTGRES_HOST"),
            PORT=env("POSTGRES_PORT"),
            NAME=env("POSTGRES_DB"),
        ),
        Redis=RedisStorge(HOST=env("REDIS-HOST"), PORT=env("REDIS-PORT")),
        AdminId=Admins(
            ADMINID=list(
                int(adm_id) for adm_id in map(lambda admins: admins.strip(), env("ADMIN-ID").split(",")) if adm_id
            )
        ),
        SecretKey=SecretKey(SECRETKEY=env("SECRETKEY").encode("utf-8")),
        TronGridAPI=TronGridAPI(APIKEY=env("TRON-GRID-API")),
    )
