import datetime
import random
from typing import Any, Sequence

from sqlalchemy import RowMapping
from sqlalchemy.engine import Row

from databaseAPI.commands.submissions_commands import SubmissionsAPI
from databaseAPI.commands.userCommands.admin_commands import AdminAPI
from databaseAPI.models import Submissions
from databaseAPI.models.models import Statuses, Users
from services.cryptoService import CryptoCheck


class UserService:
    @staticmethod
    async def random_admin() -> Users | None:
        """
        :return: (Users | None) A random administrator with a WorkType=True
        """
        all_work_admins: list[Users] = await AdminAPI.select_work_admins()
        return random.choice(all_work_admins) if all_work_admins else None

    @staticmethod
    async def format_date_string(date: datetime.datetime) -> str | None:
        """
        Formats the date into a nicer look
        :param date: (datetime.datetime)
        :return: (str | None)
        """
        formatted_string = None
        if date:
            formatted_string = date.strftime("%Y %B %d %H:%M")
        return formatted_string

    @staticmethod
    async def statistic_user(user_id: int) -> dict[str, Any]:
        """
        Returns the user's statistics
        :param user_id: (int) user id
        :return: (dict[str: Any])"""
        favorite_category: dict[str:int] = dict()
        count_each_mission: dict[str:int] = {
            Statuses.wait.value: 0,
            Statuses.accepted.value: 0,
            Statuses.completed.value: 0,
        }
        user_missions: Sequence[Row | RowMapping | Any] = await SubmissionsAPI.select_missions(
            False, user_id, 0, Submissions
        )
        count_transaction: int = len(user_missions)
        total_amount: float = 0.0
        for mission in user_missions:
            favorite_category[mission.TypeTrans.value] = favorite_category.get(mission.TypeTrans.value, 0) + 1
            count_each_mission[mission.Status.value] = count_each_mission.get(mission.Status.value, 0) + 1
            if mission.Status == Statuses.completed:
                amount_from = (
                    await CryptoCheck.transaction_amount(
                        amount=mission.AmountTo,
                        currency_from=mission.CurrencyTo,
                        currency_to="RUB",
                        margins=1,
                    )
                    if mission.CurrencyTo != "СБП"
                    else mission.AmountTo
                )
                total_amount += amount_from
        return {
            **count_each_mission,
            "countTransaction": count_transaction,
            "totalAmount": total_amount,
            "averageAmount": (
                round(total_amount / count_each_mission[Statuses.completed.value], 2)
                if count_each_mission[Statuses.completed.value]
                else 0
            ),
            "typeTransaction": max(favorite_category) if favorite_category else None,
        }

    @staticmethod
    async def verif_number() -> int:
        """
        Returns a random number to pass KYC
        :return: (int)
        """
        return random.randint(10**5, 10**6 - 1)

    @staticmethod
    async def statistic_admin() -> dict[str:Any]:
        """
        Returns statistics for admins
        :return: (dict[str: Any])
        """
        completed_submissions: Sequence[Row] = await SubmissionsAPI.select_missions(
            False, None, 0, *(Submissions,), Status=Statuses.completed
        )
        result = {
            "gainToDay": 0,
            "gainToWeek": 0,
            "gainToMonth": 0,
            "gainTotal": 0,
            "maxExchangeAmount": 0,
            "maxExchangeUserID": 0,
            "maxExchangeDateTime": None,
        }
        cache_currency: dict[int, float] = {"СБП": 1, "RUB": 1}
        now = datetime.datetime.utcnow()
        today = now - datetime.timedelta(days=1)
        toweek = now - datetime.timedelta(weeks=1)
        tomonth = now - datetime.timedelta(days=30)
        for mission in completed_submissions:
            amount_user = mission.AmountFrom
            wallet, user = mission.wallet, mission.user
            if cache_currency.get(wallet.NameNet) is None:
                cache_currency[wallet.NameNet] = await CryptoCheck.currency_rate(
                    currency_to=wallet.NameNet, currency_from="RUB", margins=1
                )
            amount_user *= cache_currency[wallet.NameNet]
            amount_admin = amount_user * (wallet.Percent - 1)
            if mission.created_at >= today:
                result["gainToDay"] += amount_admin
            if mission.created_at >= toweek:
                result["gainToWeek"] += amount_admin
            if mission.created_at >= tomonth:
                result["gainToMonth"] += amount_admin
            if result["maxExchangeAmount"] < amount_user:
                result["maxExchangeAmount"] = amount_user
                result["maxExchangeUserID"] = user.UserId
                result["maxExchangeDateTime"] = mission.created_at
            result["gainTotal"] += amount_admin
        result["gainToDay"] = round(result["gainToDay"], 2)
        result["gainToWeek"] = round(result["gainToWeek"], 2)
        result["gainToMonth"] = round(result["gainToMonth"], 2)
        result["gainTotal"] = round(result["gainTotal"], 2)
        result["maxExchangeDateTime"] = await UserService.format_date_string(date=result["maxExchangeDateTime"])
        return result
