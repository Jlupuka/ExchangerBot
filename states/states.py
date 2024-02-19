from aiogram.filters.state import State, StatesGroup


class FSMFiatCrypto(StatesGroup):
    crypto_to = State()
    requisites = State()
    check_validate = State()
    method = State()


class FSMCryptoFiat(StatesGroup):
    crypto_from = State()
    requisites = State()


class FSMCryptoCrypto(StatesGroup):
    crypto_from = State()
    crypto_to = State()
    requisites = State()


class FSMAddWallet(StatesGroup):
    crypto_to = State()
    address = State()
    type_wallet = State()
    check_correct = State()


class FSMPercentEdit(StatesGroup):
    get_percent = State()
    check_percent = State()
