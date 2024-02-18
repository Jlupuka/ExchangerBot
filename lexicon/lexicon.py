LexiconCommands: dict[str: str] = {
    '/start': 'Запуск работы бота',
    '/help': 'Помощь с взаимодействием бота',
}

botMessages: dict[str: str] = {
    'anyMessage': 'Введите /start или /help',
    'startMessageAdmin': '''
<i><u>Здравствуй, Администратор</u></i>⚖️
Вас приветствует стартовое меню бота <b>Exchanger</b>💱
🔗 В случае вопросов пишите гл.администратору: @floix''',
    'startMessageUser': '''<i><u>Здравствуйте</u></i>👋
Вас приветствует бот <b>Exchanger</b>💱
Выберите, каким способом Вы хотите произвести обмен💳
🔗 В случае вопросов пишите гл.администратору: @floix''',
    'profileTextUser': '''
Ваш профиль:
...''',
    'statisticTextUser': '''Ваша статистика:''',
    'missionsTextUser': '''Выберите одно из трех состояний заявки, чтобы узнать информацию об этой категории заявок''',
    'informationMissions': 'Для того, чтобы получить информацию о заявке - <b><i>нажмите</i></b> на нее.',
    'choiceToken': 'Выберите <b><i>криптовалюту</i></b> для осуществления перевода средств🪙',
    'getAddressCrypto': '''Введите адрес Вашего <b><i>криптокошелька</i></b>.
Если хотите вернуться обратно - нажмите "Назад".
Если хотите <b><i>отменить</i></b> обмен можете ввести или нажать /cancel''',
    'checkCorrectAddress': '''🟢 Ваши данные:
<b><i>🛰️ Сеть</i></b> ⟶ <code>{net}</code>
<b><i>💳 Адрес кошелька</i></b> ⟶ <code>{wallet_address}</code>
🔶 Вы уверены, что это тот кошелек?''',
    'cancelLexicon': 'Отменить🔚',
    'choiceMethod': '''⚙️ Выберете удобный способ ввода суммы средств для перевода
или нажмите <b><i>"Отменить"</i></b> для отмены обмена.''',
    'settingsText': '''💼 Администраторов в сети: <code>{adminsWork}</code>
🗃️ Ваш статус работы: <code>{workType}</code>,
💳 Количество кошельков в базе: <code>{countWallets}</code>
📇 Количество заявок в состоянии <b><i>WAIT</i></b>: <code>{countMissions}</code>
''',
    'walletsMenu': 'Вы открыли меню рабочих кошельков.\n'
                   'Здесь Вы можете <b><i>добавить</i></b> кошелек или, нажав на одну из позиций, '
                   '<b><i>изменить данные</i></b> кошелька или <b><i>удалить</i></b> его.\n'
                   '⚙️ <i>Изменить можно</i>:\n'
                   '<b>･ <i>Статус (рабочий или нет)</i></b>\n'
                   '<b>･ <i>Процент наценки ⚖️</i></b>\n'
                   '<b>･ <i>Реквизиты 💳</i></b>\n'
                   '<b>･ <i>Тип (Fiat 💸 | Crypto 🪙)</i></b>\n',
    'addWallet': '🔶 Введите <b><u>короткое</u></b> название <b><i>валюты</i></b>',
    'getNameNet': '🔶 Введите <b><i>реквизиты</i></b>',
    'getWalletType': '🔶 Выберите <b><i>тип кошелька</i></b>',
    'backWallets': 'Вернуться 🔚',
    'checkDataAddWallet': '''Данные, которые Вы ввели:
🛰️ Валюта кошелька: <code>{nameNet}</code>
💳 Реквизиты кошелька: <code>{address}</code>
🗃️ Тип кошелька: <code>{walletType}</code>
Вы <b><i><u>уверены</u></i></b>, что это <b><i><u>верные</u></i></b> данные?
''',
    'addressMenu': '⬇️ <b><i>Выберите действие, которое хотите осуществить с данным кошельком</i></b> ⬇️',
    'sureDelete': '🔶 Вы уверены, что хотите удалить кошелек?',
    'deleteAddress': 'Вы успешно удалили кошелек <code>{wallet}</code>!',
}

errorLexicon: dict[str: str] = {
    'errorAddress': '''🔴 Вы ввели неверный адрес кошелька.
<b><i>🛰️ Сеть</i></b> ⟶ <code>{net}</code>
<b><i>💳 Адрес кошелька</i></b> ⟶ <code>{wallet_address}</code>''',
    'errorToken': '''🔴 Вы ввели неверное название валюты.
В случае, если Вы <b><i>уверены</i></b>, что введенная Вами валюта существует — напишите администратору @floix
<b><i>🛰️ Сеть</i></b> ⟶ <code>{net}</code>''',
    'WalletExist': '''🔴 Кошелек с такими данными уже <b><i><u>существуют</u></i></b>
🛰️ Валюта кошелька: <code>{nameNet}</code>
💳 Реквизиты кошелька: <code>{address}</code>
🗃️ Тип кошелька: <code>{walletType}</code>'''
}

startCallbackUser: dict[str: str] = {
    'rub-crypto': 'RUB 💸 ⟶ CRYPTO 🪙',
    'crypto-rub': 'CRYPTO 🪙 ⟶ RUB 💸',
    'crypto-crypto': 'CRYPTO 🪙 ⟶ CRYPTO 🪙',
    'info': 'Информация 📒',
    'profile': 'Профиль 🪪'
}

startCallbackAdmin: dict[str: str] = {
    'statistics': 'Статистика 📊',
    'information': 'Информация 📒',
    'instruction': 'Инструкция 📎',
    'settings': 'Настройки ⚙️',
}

profileUser: dict[str: str] = {
    'missions': 'Заявки 📨',
    'statistics': 'Статистика 📊',
}

listMissionsUser: dict[str: str] = {
    'accepted': 'Принятые 🟣',
    'completed': 'Завершенные ✅',
    'waiting': 'В ожидание 🕜'
}

choiceToken: dict[str: str] = {
    'btc': 'BTC 💳',
    'eth': 'ETH 💳'
}

checkCorrectAddress: dict[str: dict] = {
    'yes': 'Да ✅',
    'no': 'Нет ❌'
}

repeatAddress: dict[str: str] = {
    'repeat': 'Повторить 🔁'
}

choiceMethod: dict[str: str] = {
    'crypto': 'CRYPTO 🪙',
    'rub': 'RUB 🇷🇺₽',
    'usd': 'USD 🇺🇸$'
}

settingsMenu: dict[str: str] = {
    'workType': None,
    'wallets': 'Кошельки 💼',
}

workType: dict[bool: str] = {
    True: "Работаю ✅",
    False: "Не работаю ❌"
}

missions: dict[str: str] = {
    'missions': 'Заявки 📑'
}

walletsMenu: dict[str: str] = {
    'addWallet': 'Добавить 💾'
}

walletType = {
    'rub': 'RUB 💳',
    'crypto': 'CRYPTO 🪙'
}

checkCorrectAddWallet: dict[str: dict] = {
    'yes': 'Да ✅',
    'no': 'Повторить заново 🔁'
}

successfullyMessage: dict[str: str] = {
    'addWallet': '''✅ Кошелек <b><i>добавлен</i></b> в базу данных ✅
<i>Информация по нему</i>:
🛰️ Валюта кошелька: <code>{nameNet}</code>
💳 Реквизиты кошелька: <code>{address}</code>
🗃️ Тип кошелька: <code>{walletType}</code>
'''
}

addressMenu: dict[str: str] = {
    'deleteAddress': 'Удалить кошелек ❌',
    'editAddress': 'Изменить данные 🪪'
}

sureDelete: dict[str: str] = {
    'yes': 'Да ✅',
    'no': 'Отменить ❌'
}

addressDelete: dict[str: str] = {
    'wallets': 'Кошельки 📒'
}
