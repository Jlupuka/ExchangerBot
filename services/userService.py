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
    async def statistic_user(user_id: int) -> dict[str: str | int]:
        favorite_category: dict[str: int] = dict()
        count_each_mission: dict[str: int] = {
            'WAIT': 0,
            'ACCEPTED': 0,
            'COMPLETED': 0
        }
        user_missions: list[Row] = await SubmissionsAPI.get_user_missions_wallets(
            user_id=user_id)
        count_transaction: int = len(user_missions)
        total_amount: float = 0.0
        for data in user_missions:
            mission, wallet = data
            favorite_category[mission.TypeTrans] = favorite_category.get(mission.TypeTrans, 0) + 1
            count_each_mission[mission.Status] = count_each_mission.get(mission.Status, 0) + 1
            if mission.Status == 'COMPLETED':
                amount_from = await CryptoCheck.transaction_amount(amount=mission.AmountFrom,
                                                                   currency_from=wallet.NameNet,
                                                                   currency_to='RUB',
                                                                   margins=1)
                total_amount += amount_from
        return {**count_each_mission,
                'countTransaction': count_transaction,
                'totalAmount': total_amount,
                'averageAmount': round(total_amount / count_each_mission['COMPLETED'], 2),
                'typeTransaction': max(favorite_category)}
