from aiogram.filters.state import State, StatesGroup


class FSMFiatCrypto(StatesGroup):
    currency_to = State()
    requisites = State()
    check_validate = State()
    check_validate_sum = State()
    method = State()
    get_sum = State()
    money_sent = State()


class FSMCryptoFiat(StatesGroup):
    crypto_from = State()
    requisites = State()
    money_sent = State()


class FSMCryptoCrypto(StatesGroup):
    crypto_from = State()
    crypto_to = State()
    requisites = State()
    money_sent = State()


class FSMAddWallet(StatesGroup):
    currency_to = State()
    address = State()
    type_wallet = State()
    check_correct = State()


class FSMPercentEdit(StatesGroup):
    get_percent = State()
    check_percent = State()
