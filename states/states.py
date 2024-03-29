from aiogram.filters.state import State, StatesGroup


class FSMFiatCrypto(StatesGroup):
    currency_to = State()
    type_fiat = State()
    requisites = State()
    check_validate = State()
    check_validate_sum = State()
    method = State()
    get_sum_crypto = State()
    get_sum = State()
    money_sent = State()


class FSMCryptoFiat(StatesGroup):
    check_validate_sum = State()
    check_validate = State()
    currency_to = State()
    type_crypto = State()
    requisites = State()
    money_sent = State()
    get_sum = State()
    get_sum_crypto = State()
    method = State()


class FSMCryptoCrypto(StatesGroup):
    check_validate_sum = State()
    check_validate = State()
    type_crypto = State()
    currency_to = State()
    requisites = State()
    money_sent = State()
    get_sum_crypto = State()
    get_sum = State()
    method = State()


class FSMAddWallet(StatesGroup):
    currency_to = State()
    address = State()
    mnemonic = State()
    type_wallet = State()
    check_correct = State()


class FSMPercentEdit(StatesGroup):
    get_percent = State()
    check_percent = State()


class FSMRevokeMission(StatesGroup):
    sure = State()
    message = State()


class FSMVerify(StatesGroup):
    get_photo = State()


class FSMEditMinSum(StatesGroup):
    get_sum = State()
    check_sure = State()


class FSMEditPatterns(StatesGroup):
    get_pattern = State()
    get_token_name = State()
    choice_pattern = State()
    check_sure = State()
