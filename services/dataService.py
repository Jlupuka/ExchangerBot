from typing import Any

import aiofiles
import json

from services.cardService import CardCheck


class JsonService:
    @staticmethod
    async def save_json(data: dict[str:Any], file: str = "src/data/data.json") -> None:
        async with aiofiles.open(file, mode="w", encoding="utf-8") as f:
            await f.write(json.dumps(data, indent=4))

    @staticmethod
    async def read_json(filename: str = "src/data/data.json") -> dict:
        async with aiofiles.open(filename, mode="r", encoding="utf-8") as f:
            return json.loads(await f.read())

    @staticmethod
    async def get_token_patterns() -> dict[str:str]:
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
        return (await JsonService.read_json())[name_data]

    @staticmethod
    async def save_token_patterns(patterns: dict[str:str]) -> None:
        json_data: dict[str:Any] = await JsonService.read_json()
        if patterns.get("rub"):
            patterns.pop("rub")
        json_data["patterns"] = {key: data for key, data in patterns.items()}
        await JsonService.save_json(data=json_data)

    @staticmethod
    async def preprocess_patterns_for_button() -> dict[str:str]:
        patterns = await JsonService.get_specific_data("patterns")
        return {key: key.upper() for key in patterns.keys()}

    @staticmethod
    async def preprocess_patterns_for_text() -> str:
        result = list()
        patterns: dict[str:str] = await JsonService.get_specific_data("patterns")
        for key, pattern in patterns.items():
            result.append(f"<b>{key.upper()}</b> - <code>{pattern}</code>")
        return "\n".join(result)
