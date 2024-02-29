import random
from databaseAPI.commands.userCommands.admin_commands import AdminAPI
from databaseAPI.tables.usersTable import Users


class UserService:
    @staticmethod
    async def random_admin() -> Users | None:
        all_work_admins: list[Users] = await AdminAPI.select_all_admins()
        return random.choice(all_work_admins) if all_work_admins else None
