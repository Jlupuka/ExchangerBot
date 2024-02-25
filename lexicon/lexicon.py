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
    'checkDataAddWallet': '''Данные, которые Вы ввели:
🛰️ Валюта кошелька: <code>{nameNet}</code>
💳 Реквизиты кошелька: <code>{address}</code>
🗃️ Тип кошелька: <code>{walletType}</code>
Вы <b><i><u>уверены</u></i></b>, что это <b><i><u>верные</u></i></b> данные?
''',
    'addressMenu': '⬇️ <b><i>Выберите действие, которое хотите осуществить с данным кошельком</i></b> ⬇️',
    'sureDelete': '🔶 Вы уверены, что хотите удалить кошелек?',
    'deleteAddress': 'Вы успешно удалили кошелек <code>{wallet}</code>!',
    'addressEdit': '''📑 <b><i>Информация по кошельку</i></b>:
💳 Реквизиты ⟶ <code>{address}</code>
💼 Состояние кошелька ⟶ <code>{workType}</code>
⚖️ Процент наценки ⟶ <code>{percent}</code>''',
    'getPercent': '🔶 Вы уверены, что это верный процент - <code>{percent}</code>',
    'percentEdit': '📝 Напишите процент, который будет стоять на этом кошельке в виде комиссии',
    'completedEditPercent': '''🟢 Процент успешно сохранен! ✅
<b><i>Новый процент</i></b>: <code>{percent}</code>''',
    'getSum': '''Напишите сумму перевода, который хотите совершить для обмена.
💳 <i>Минимальный ввод</i>: <code>{min_sum} {currency_from}</code> 
⚖️ Курс <i><b>{currency_to}</b></i> ⟶ <i><b>{currency_from}</b></i> = <code>{currency_rate}</code>''',
    'checkTheCorrectTransaction': '''📝 <b>Данные по сделки:</b>
<b><i>💱 Валюта в которой придут деньги:</i></b> <code>{name_net}</code>
<b><i>🪪 Кошелек куда придут деньги:</i></b> <code>{address}</code>
<b><i>💳 Сумма к оплате:</i></b> <code>{amount_from} {currency_from}</code>
<b><i>💸 Сумма к получению:</i></b> <code>{amount_to} {currency_to}</code>
<u><i><b>🔶 Все верно?</b></i></u>
''',
    'receiptVerification': '''💼 <i>Для получения <code>{amount_to}</code> <b>{currency_to}</b>
📨 Переведите <code>{amount_from}</code> <b>{type_transaction}</b>
💳 На эти реквизиты ⟶ <code>{work_wallet}</code></i>

<b>                     📌 <u>ВНИМАНИЕ</u> 📌

🖍️ <u><i>НЕ УДАЛЯЙТЕ</i></u> это сообщение!
📜 Для того, чтобы Ваша заявка вступила в силу ⬇️
･ <u><i>ОБЯЗАТЕЛЬНО, после</i></u> отправки средств надо нажать на кнопку "Отправил ✅".
</b>''',
    'createMission': '''<i>Вы успешно создали заявку на обмен!</i>
<b>⬇️ Данные по сделке ⬇️
📝 <i>Номер сделки</i> ⟶ <code>#{mission_id}</code>
💳 <i>Реквизиты куда придут средства</i> ⟶ <code>{user_requisites}</code>
💸 <i>Сумма средств, подлежащая зачислению на Ваш кошелек</i> ⟶ <code>{amount} {currency_to}</code></b>
'''
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
🗃️ Тип кошелька: <code>{walletType}</code>''',
    'IsDigit': '''🔴 <b>ОШИБКА</b> 🔴
Не верное сообщение, не является числом - <code>{digit}</code>''',
    'getSum_minimal': '''🔴 <b>ОШИБКА</b> 🔴 
<code>{amount}</code> <b>{currency_from}</b> - меньше допустимого значения.'''
}

startCallbackUser: dict[str: str] = {
    'rub-crypto': 'RUB 💸 ⟶ CRYPTO ₿',
    'crypto-rub': 'CRYPTO ₿ ⟶ RUB 💸',
    'crypto-crypto': 'CRYPTO ₿ ⟶ CRYPTO ₿',
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
    'crypto': 'CRYPTO ₿',
    'rub': '🇷🇺 RUB ₽',
    'usd': '🇺🇸 USD $'
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
    'addressEdit': 'Изменить данные 🪪'
}

sureLexicon: dict[str: str] = {
    'yes': 'Да ✅',
    'no': 'Отменить ❌'
}

addressDelete: dict[str: str] = {
    'wallets': 'Кошельки 📒'
}

addressEdit: dict[str: str] = {
    'statusWork': '',
    'percentEdit': 'Изменить процент ⚖️'
}

statusWork: dict[str: str] = {
    True: 'Работает ✅',
    False: 'Не работает ❌'
}

backLexicon: dict[str: str] = {
    'cancelLexicon': 'Отменить 🔚',
    'backLexicon': 'Вернуться 🔚',
    'backMainMenu': 'Главное меню 🔚'
}

repeatGetPercent: dict[str: str] = {
    'repeatGetPercent': 'Повторить 🔁'
}

checkData: dict[str: str] = {
    'choiceMethod': 'Да ✅'
}

cryptoSymbol: dict[str: str] = {
    'symbol': '🪙'
}

minSum: dict[str: str] = {
    'minSum': '💱 Минимальная сумма'
}

getSum: dict[str: str] = {
    'getSum': 'Да ✅',
    'repeatGetSum': 'Повторить ввод 🔁'
}

receiptVerification: dict[str: str] = {
    'sent': 'Отправил ✅'
}

repeatGetSum: dict[str: str] = {
    'repeatGetSum': 'Повторить ввод 🔁'
}
