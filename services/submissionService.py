from databaseAPI.commands.submissions_commands import SubmissionsAPI
from databaseAPI.tables import Submissions


class SubmissionService:
    @staticmethod
    async def preprocess_mission_data(
        mission_data: list[Submissions],
    ) -> tuple[str, dict[str:str]]:
        result_dict = dict()
        result_text = list()
        for mission in sorted(mission_data, key=lambda data: data.Id):
            result_dict[f"{mission.Id}"] = (
                f"🆔 {mission.Id} | 📑 {mission.TypeTrans}"
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
            count_mission: int = await SubmissionsAPI.get_count_missions_by_status(
                mission_status=missionStatus
            )
            text = f"<i>Количество <b>{missionStatus}</b> ⟶ <code>{count_mission}</code></i>"
            result.append(text)
        return "\n".join(result)
