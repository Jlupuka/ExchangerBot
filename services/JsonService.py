import glob
import json
from typing import Any, Union

import os
import aiofiles

from dataTemplates.data_templates import WalletTRX
from services.cardService import CardCheck


__basedir__ = "src/data/"


class JsonService:
    @staticmethod
    async def save_json(data: dict[str:Any], filename: str = "data.json") -> None:
        """
        Asynchronously saves json
        :param data: (dict[str:Any])
        :param filename: (str) file where the data will be saved. The base folder is "src/data/"
        :return:
        """
        async with aiofiles.open(
            f"{__basedir__}/{filename}", mode="w", encoding="utf-8"
        ) as f:
            await f.write(json.dumps(data, indent=4, ensure_ascii=False))

    @staticmethod
    async def read_json(filename: str = "data.json") -> dict[str:Any]:
        """
        Pulls data from json
        :param filename: (str) file where the data will be taken from. The base folder is "src/data/"
        :return: (dict[str:Any])
        """
        async with aiofiles.open(
            f"{__basedir__}/{filename}", mode="r", encoding="utf-8"
        ) as f:
            return json.loads(await f.read())

    @staticmethod
    async def get_token_patterns() -> dict[str:str]:
        """
        Returns all tokens of cryptocurrency patterns
        :return: (dict[str:str])
        """
        token_patterns = {
            "rub": CardCheck.validate_luhn,
            **{
                key: pattern
                for key, pattern in (
                    await JsonService.get_specific_data(name_data="patterns")
                ).items()
            },
        }
        return token_patterns

    @staticmethod
    async def get_specific_data(name_data: str) -> dict[str:str]:
        """
        Returns data from json by key
        :param name_data: (str) json key
        :return: (dict[str:str])
        """
        return (await JsonService.read_json())[name_data]

    @staticmethod
    async def save_token_patterns(patterns: dict[str:str]) -> None:
        """
        Saves a new pattern dictionary for tokens
        :param patterns: (dict[str:str]) pattern dictionary
        :return:
        """
        json_data: dict[str:Any] = await JsonService.read_json()
        if patterns.get("rub"):
            patterns.pop("rub")
        json_data["patterns"] = {key: data for key, data in patterns.items()}
        await JsonService.save_json(data=json_data)

    @staticmethod
    async def preprocess_patterns_for_button() -> dict[str:str]:
        """
        Convert patterns to create buttons
        :return: (dict[patterns.key:patterns.key.upper()])
        """
        patterns = await JsonService.get_specific_data("patterns")
        return {key: key.upper() for key in patterns.keys()}

    @staticmethod
    async def preprocess_patterns_for_text() -> str:
        """
        Convert patterns to text
        :return: (str) Information about patterns
        """
        result = list()
        patterns: dict[str:str] = await JsonService.get_specific_data("patterns")
        for key, pattern in patterns.items():
            result.append(f"<b>{key.upper()}</b> - <code>{pattern}</code>")
        return "\n".join(result)

    @staticmethod
    async def save_work_wallets_data(token: str, wallet_data: Union[WalletTRX]) -> None:
        """
        Saves data about the working wallet in json, in order not to lose funds in case of errors
        :param token: (str) token cryptocurrency
        :param wallet_data: (Union[WalletTRX]) Wallet data template
        :return:
        """
        wallets_data: dict[str:list[dict[str:str]]] = await JsonService.read_json(
            filename="workWalletsData.json"
        )
        token_data = wallets_data.get(token, [])
        token_data.append({**wallet_data.__dict__})
        wallets_data[token] = token_data
        await JsonService.save_json(data=wallets_data, filename="workWalletsData.json")

    @staticmethod
    async def load_copy_json() -> None:
        """
        Loads all "copy_*.json" in non-copy and saves in src/data/ directory
        :return: None
        """
        for filename in glob.glob(os.path.join(__basedir__, "copy_*.json")):
            new_filename = filename.replace(f"{__basedir__}copy_", "")
            if not os.path.isfile(filename):
                copy_any_data = await JsonService.read_json(filename=new_filename)
                await JsonService.save_json(data=copy_any_data, filename=new_filename)
