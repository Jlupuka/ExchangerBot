from typing import Any, Sequence

from sqlalchemy import Row, RowMapping

from databaseAPI.commands.submissions_commands import SubmissionsAPI
from databaseAPI.models import Submissions
from databaseAPI.models.models import Statuses


class SubmissionService:
    @staticmethod
    async def preprocess_mission_data(
        mission_data: Sequence[Row | RowMapping | Any],
    ) -> tuple[str, dict[str:str]]:
        """
        Returns converted data for issuing missions data to administrators
        :param mission_data: (Sequence[Submissions])
        :return: (tuple[str, dict[str:str]]) first value - text message, second value - data for buttons
        """
        result_dict = dict()
        result_text = list()
        for mission in sorted(mission_data, key=lambda data: data.Id):
            result_dict[f"{mission.Id}"] = (
                f"🆔 {mission.Id} | 📑 {mission.TypeTrans.value}"
                f" | 💳 {mission.AddressUser[:4]}...{mission.AddressUser[-4:]}"
            )
            result_text.append(
                f"<code>🆔 {mission.Id} | 💸 {mission.AmountTo} "
                f"| 💱 {mission.CurrencyTo} "
                f"| 💳 {mission.AddressUser[:6]}...{mission.AddressUser[-4:]}</code>\n"
            )
        return "".join(result_text), result_dict

    @staticmethod
    async def get_count_each_missions() -> str:
        """
        Returns the number of submissions of each type
        :return: (str)
        """
        result: list = list()
        for missionStatus in (Statuses.wait, Statuses.accepted, Statuses.completed):
            count_mission: int = len(
                await SubmissionsAPI.select_missions(False, None, 0, *(Submissions,), Status=missionStatus)
            )
            text = f"<i>Количество <b>{missionStatus.value}</b> ⟶ <code>{count_mission}</code></i>"
            result.append(text)
        return "\n".join(result)
