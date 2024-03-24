import random
import datetime

from sqlalchemy.engine import Row

from databaseAPI.commands.submissions_commands import SubmissionsAPI
from databaseAPI.commands.userCommands.admin_commands import AdminAPI
from databaseAPI.tables.usersTable import Users
from services.cryptoService import CryptoCheck


class UserService:
    @staticmethod
    async def random_admin() -> Users | None:
        all_work_admins: list[Users] = await AdminAPI.select_all_admins()
        return random.choice(all_work_admins) if all_work_admins else None

    @staticmethod
    async def format_date_string(date_string: str) -> str:
        dt_obj = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S.%f")
        formatted_string = dt_obj.strftime("%Y %B %d %H:%M")
        return formatted_string

    @staticmethod
    async def statistic_user(user_id: int) -> dict[str, int]:
        favorite_category: dict[str:int] = dict()
        count_each_mission: dict[str:int] = {"WAIT": 0, "ACCEPTED": 0, "COMPLETED": 0}
        user_missions: list[Row] = await SubmissionsAPI.get_user_missions_wallets(
            user_id=user_id
        )
        count_transaction: int = len(user_missions)
        total_amount: float = 0.0
        for data in user_missions:
            mission, wallet = data
            favorite_category[mission.TypeTrans] = (
                favorite_category.get(mission.TypeTrans, 0) + 1
            )
            count_each_mission[mission.Status] = (
                count_each_mission.get(mission.Status, 0) + 1
            )
            if mission.Status == "COMPLETED":
                amount_from = (
                    await CryptoCheck.transaction_amount(
                        amount=mission.AmountFrom,
                        currency_from=wallet.NameNet,
                        currency_to="RUB",
                        margins=1,
                    )
                    if wallet.NameNet != "СПБ"
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
        return random.randint(10**5, 10**6 - 1)

    @staticmethod
    async def statistic_admin() -> dict:
        data: list[Row] = await SubmissionsAPI.data_completed_submissions()
        result = {
            "gainToDay": 0,
            "gainToWeek": 0,
            "gainToMonth": 0,
            "gainTotal": 0,
            "maxExchangeAmount": 0,
            "maxExchangeUserID": 0,
            "maxExchangeDateTime": 0,
        }
        cache_currency: dict[int, float] = {"СПБ": 1, "RUB": 1}
        now = datetime.datetime.utcnow()
        for mission, wallet, user in data:
            amount_user = mission.AmountFrom
            if cache_currency.get(wallet.NameNet) is None:
                cache_currency[wallet.NameNet] = await CryptoCheck.currency_rate(
                    currency_to=wallet.NameNet, currency_from="RUB", margins=1
                )
            amount_user *= cache_currency[wallet.NameNet]
            amount_admin = amount_user * (wallet.Percent - 1)
            if mission.DateTime >= now - datetime.timedelta(days=1):
                result["gainToDay"] += amount_admin
            if mission.DateTime >= now - datetime.timedelta(weeks=1):
                result["gainToWeek"] += amount_admin
            if mission.DateTime >= now - datetime.timedelta(days=30):
                result["gainToMonth"] += amount_admin
            if result["maxExchangeAmount"] < amount_user:
                result["maxExchangeAmount"] = amount_user
                result["maxExchangeUserID"] = user.UserId
                result["maxExchangeDateTime"] = mission.DateTime
            result["gainTotal"] += amount_admin
        result["gainToDay"] = round(result["gainToDay"], 2)
        result["gainToWeek"] = round(result["gainToWeek"], 2)
        result["gainToMonth"] = round(result["gainToMonth"], 2)
        result["gainTotal"] = round(result["gainTotal"], 2)
        result["maxExchangeDateTime"] = await UserService.format_date_string(
            date_string=str(result["maxExchangeDateTime"])
        )
        return result
