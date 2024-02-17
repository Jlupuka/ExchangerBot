from databaseAPI.commands.walletAddress_commands import get_all_wallets
from databaseAPI.tables import WalletAddress


async def get_wallets() -> dict[str: str]:
    wallets_data: list[WalletAddress] = await get_all_wallets()
    return {wallet.lower(): wallet.upper() for wallet in wallets_data}


async def get_size_wallet(len_wallet: int) -> tuple[int, ...]:
    result_wallet_size = list()
    for index in range(len_wallet):
        if index % 3 == 1:
            result_wallet_size.append(2)
        elif index % 3 == 2:
            result_wallet_size.append(1)
    return tuple(result_wallet_size + [1, 1])
