LexiconCommands: dict[str: str] = {
    '/start': 'Запуск работы бота',
    '/help': 'Помощь с взаимодействием бота',
}

botMessages: dict[str: str] = {
    'anyMessage': 'Введите /start или /help',
    'startMessageAdmin': '''
<i><u>Здравствуй, Администратор</u></i>⚖️
Вас приветствует стартовое меню бота <b>Exchanger</b>💱
🔗В случае вопросов пишите гл.администратору: @floix''',
    'startMessageUser': '''<i><u>Здравствуйте</u></i>👋 Вас приветствует бот <b>Exchanger</b>💱
Выберите, каким способом Вы хотите произвести обмен💳
🔗В случае вопросов пишите гл.администратору: @floix''',
    'profileTextUser': '''
Ваш профиль:
...''',
    'statisticTextUser': '''Ваша статистика:''',
    'missionsTextUser': '''Выберите одно из трех состояний заявки, чтобы узнать информацию об этой категории заявок''',
    'informationMissions': 'Для того, чтобы получить информацию о заявке - <b><i>нажмите</i></b> на нее.',
}

startCallbackUser: dict[str: str] = {
    'rub-crypto': 'RUB💸/CRYPTO🪙',
    'crypto-rub': 'CRYPTO🪙/RUB💸',
    'crypto-crypto': 'CRYPTO🪙/CRYPTO🪙',
    'info': 'Информация📒',
    'profile': 'Профиль🪪'
}

startCallbackAdmin: dict[str: str] = {
    'statistics': 'Статистика📊',
    'information': 'Информация📒',
    'instruction': 'Инструкция📎',
    'settings': 'Настройки⚙️',
}

profileUser: dict[str: str] = {
    'missions': 'Заявки📨',
    'statistics': 'Статистика📊',
}

listMissionsUser: dict[str: str] = {
    'accepted': 'Принятые🟣',
    'completed': 'Завершенные✅',
    'waiting': 'В ожидание🕜'
}
