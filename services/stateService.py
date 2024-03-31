from aiogram.fsm.context import FSMContext

from states.states import FSMCryptoCrypto, FSMCryptoFiat, FSMFiatCrypto


class StateService:
    @staticmethod
    async def set_states(state_name: str, state_data: dict[str:str], state: FSMContext) -> None:
        """
        A function that sets the state for a particular FSM
        :param state_name: (str) Name of the state to switch to
        :param state_data: (dict[str: str) State data
        :param state: (aiogram.fsm.context.FSMContext)
        :return: None
        """
        match state_data["typeTransaction"]:
            case "RUB-CRYPTO":
                await state.set_state(getattr(FSMFiatCrypto, state_name))
            case "CRYPTO-RUB":
                await state.set_state(getattr(FSMCryptoFiat, state_name))
            case "CRYPTO-CRYPTO":
                await state.set_state(getattr(FSMCryptoCrypto, state_name))
