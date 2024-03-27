import random
import datetime
from typing import Sequence, Any

from sqlalchemy import RowMapping
from sqlalchemy.engine import Row

from databaseAPI.commands.submissions_commands import SubmissionsAPI
from databaseAPI.commands.userCommands.admin_commands import AdminAPI
from databaseAPI.models import Wallets, Submissions
from databaseAPI.models.models import Users, Statuses
from services.cryptoService import CryptoCheck


class UserService:
    @staticmethod
    async def random_admin() -> Users | None:
        all_work_admins: list[Users] = await AdminAPI.select_work_admins()
        return random.choice(all_work_admins) if all_work_admins else None

    @staticmethod
    async def format_date_string(date: datetime.datetime) -> str | None:
        formatted_string = None
        if date:
            formatted_string = date.strftime("%Y %B %d %H:%M")
        return formatted_string

    @staticmethod
    async def statistic_user(user_id: int) -> dict[str, int]:
        favorite_category: dict[str:int] = dict()
        count_each_mission: dict[str:int] = {"WAIT": 0, "ACCEPTED": 0, "COMPLETED": 0}
        user_missions: Sequence[Row | RowMapping | Any] = await SubmissionsAPI.select_missions(False, user_id, 0,
                                                                                               Submissions, Wallets)
        count_transaction: int = len(user_missions)
        total_amount: float = 0.0
        for mission in user_missions:
            favorite_category[mission.TypeTrans.value] = (
                    favorite_category.get(mission.TypeTrans, 0) + 1
            )
            count_each_mission[mission.Status.value] = (
                    count_each_mission.get(mission.Status, 0) + 1
            )
            if mission.Status == Statuses.completed:
                amount_from = (
                    await CryptoCheck.transaction_amount(
                        amount=mission.AmountFrom,
                        currency_from=mission.wallet.NameNet,
                        currency_to="RUB",
                        margins=1,
                    )
                    if mission.wallet.NameNet != "СПБ"
                    else mission.AmountFrom
                )
                total_amount += amount_from
        return {
            **count_each_mission,
            "countTransaction": count_transaction,
            "totalAmount": total_amount,
            "averageAmount": (
                round(total_amount / count_each_mission["COMPLETED"], 2)
                if count_each_mission["COMPLETED"]
                else 0
            ),
            "typeTransaction": max(favorite_category) if favorite_category else None,
        }

    @staticmethod
    async def verif_number() -> int:
        return random.randint(10 ** 5, 10 ** 6 - 1)

    @staticmethod
    async def statistic_admin() -> dict:
        completed_submissions: Sequence[Row] = await SubmissionsAPI.select_missions(False,
                                                                                    None,
                                                                                    0,
                                                                                    *(Submissions,),
                                                                                    Status=Statuses.completed)
        result = {
            "gainToDay": 0,
            "gainToWeek": 0,
            "gainToMonth": 0,
            "gainTotal": 0,
            "maxExchangeAmount": 0,
            "maxExchangeUserID": 0,
            "maxExchangeDateTime": None,
        }
        cache_currency: dict[int, float] = {"СПБ": 1, "RUB": 1}
        now = datetime.datetime.utcnow()
        for mission in completed_submissions:
            amount_user = mission.AmountFrom
            wallet, user = mission.wallet, mission.user
            if cache_currency.get(wallet.NameNet) is None:
                cache_currency[wallet.NameNet] = await CryptoCheck.currency_rate(
                    currency_to=wallet.NameNet, currency_from="RUB", margins=1
                )
            amount_user *= cache_currency[wallet.NameNet]
            amount_admin = amount_user * (wallet.Percent - 1)
            if mission.created_at >= now - datetime.timedelta(days=1):
                result["gainToDay"] += amount_admin
            if mission.created_at >= now - datetime.timedelta(weeks=1):
                result["gainToWeek"] += amount_admin
            if mission.created_at >= now - datetime.timedelta(days=30):
                result["gainToMonth"] += amount_admin
            if result["maxExchangeAmount"] < amount_user:
                result["maxExchangeAmount"] = amount_user
                result["maxExchangeUserID"] = user.UserId
                result["maxExchangeDateTime"]: datetime = mission.created_at
            result["gainTotal"] += amount_admin
        result["gainToDay"] = round(result["gainToDay"], 2)
        result["gainToWeek"] = round(result["gainToWeek"], 2)
        result["gainToMonth"] = round(result["gainToMonth"], 2)
        result["gainTotal"] = round(result["gainTotal"], 2)
        result["maxExchangeDateTime"] = await UserService.format_date_string(
            date=result["maxExchangeDateTime"]
        )
        return result
