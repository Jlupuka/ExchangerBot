from databaseAPI.commands.walletAddress_commands import get_all_wallets
from databaseAPI.tables import WalletAddress


async def get_wallets() -> dict[str: str]:
    wallets_data: set[str] = await get_all_wallets()
    return {wallet.lower(): wallet.upper() for wallet in wallets_data}


async def get_size_wallet(len_wallet: int, count_any_button: int = 0) -> tuple[int, ...]:
    result_wallet_size = list()
    for index in range(len_wallet):
        if index % 3 == 1:
            result_wallet_size.append(2)
        elif index % 3 == 2:
            result_wallet_size.append(1)
    return tuple(result_wallet_size + [1] * count_any_button)


async def preprocess_wallets(wallets: list[tuple[int, str]]) -> tuple[str, dict[str: str]]:
    result_text = str()
    result_dict = dict()
    line_feed = '\n'
    for index in range(len_wallets := len(wallets)):
        result_text += (f'{wallets[index][0]}. <code>{wallets[index][1]}'
                        f'</code>{"" if index == len_wallets - 1 else line_feed}')
        result_dict[f'id-{wallets[index][0]}'] = str(wallets[index][0])
    return result_text, {address_id: result_dict[address_id] for address_id in sorted(result_dict)}
