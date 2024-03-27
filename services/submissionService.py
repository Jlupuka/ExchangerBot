from typing import Sequence, Any

from sqlalchemy import RowMapping, Row

from databaseAPI.commands.submissions_commands import SubmissionsAPI
from databaseAPI.models import Submissions
from databaseAPI.models.models import Statuses


class SubmissionService:
    @staticmethod
    async def preprocess_mission_data(
        mission_data: Sequence[Row | RowMapping | Any]
    ) -> tuple[str, dict[str:str]]:
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
        result: list = list()
        for missionStatus in ("WAIT", "ACCEPTED", "COMPLETED"):
            mission_status: Statuses = Statuses[missionStatus.lower()]
            count_mission: int = len(await SubmissionsAPI.select_missions(
                False,
                None,
                0,
                *(Submissions,),
                Status=mission_status
            ))
            text = f"<i>Количество <b>{missionStatus}</b> ⟶ <code>{count_mission}</code></i>"
            result.append(text)
        return "\n".join(result)
