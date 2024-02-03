from aiogram.filters.state import State, StatesGroup


class FSMFiatCrypto(StatesGroup):
    crypto_to = State()
    requisites = State()


class FSMCryptoFiat(StatesGroup):
    crypto_from = State()
    requisites = State()


class FSMCryptoCrypto(StatesGroup):
    crypto_from = State()
    crypto_to = State()
    requisites = State()
