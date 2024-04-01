import json
from typing import Any

from aiogram import Router, F
from aiogram.types import CallbackQuery
from redis.asyncio.client import Redis

from factories.factory import UserCallbackFactory
from keyboard.keyboard_factory import Factories
from lexicon.lexicon import botMessages
from services.userService import UserService

router: Router = Router()


@router.callback_query(UserCallbackFactory.filter(F.page == "statistics"))
async def statistics_handler(
    callback: CallbackQuery, callback_data: UserCallbackFactory, redis: Redis
) -> None:
    match (data := (await redis.get(f"{callback.from_user.id}:statistic"))):
        case None:
            data: dict[str:Any] = await UserService.statistic_user(
                user_id=callback.from_user.id
            )
            await redis.setex(
                name=f"{callback.from_user.id}:statistic",
                time=120,
                value=json.dumps(data),
            )
        case _:
            data: dict[str:Any] = json.loads(data)
    await callback.message.edit_text(
        text=botMessages["statisticTextUser"].format(**data),
        reply_markup=await Factories.create_fac_menu(
            UserCallbackFactory, back_page="main", back=callback_data.back_page
        ),
    )
