LexiconCommands: dict[str:str] = {
    "/start": "Запуск работы бота",
    "/help": "Помощь с взаимодействием бота",
}

botMessages: dict[str:str] = {
    "anyMessage": "Введите /start или /help",
    "informationUser": """
<b><i>Здравствуйте, Вас встречает бот обменник валют - @{botName}</i>
В нем Вы можете обменять как <u>фиатные</u> 💸 средства, так и <u>криповалюту</u> 🪙.
Обмен происходит в <i>полу-автоматическом</i> формате.
🟨 Вы присылаете средства на выданный ботом кошелек и после подтверждения платежа заявка отправляется Администраторам.
💲 Администраторы, находящиеся в сети оперативно обработают Вашу заявку и отправят средства в валюте на Ваш кошелек.</b>
""",
    "informationAdmin": """
<b><i>Здравствуйте, Вас встречает бот обменник валют - @{botName}</i>
В нем Вы, как Администратор должны обрабатывать заявки на обмена <u>фиата</u> 💸 и <u>криптовалюты</u> 🪙</b>""",
    "instructionAdmin": """
🟪 <b>Обмен происходит в <i>полу-автоматическом</i> формате.
Пользователь присылает средства на выданный ботом кошелек и после заявка отправляется Вам.
После того, как заявка дошла до Вас, <u>необходимо удостовериться</u> в приходе средств на реквизиты.
Как все средства дошли до указанного кошелька, Вы меняете статус на <i><u>ACCEPTED</u></i>.
Далее, Вы высылаете на указанные реквизиты сумму для получения пользователю.
После отправки средств, меняете статус заявки на <i><u>COMPLETED</u></i>.

🟥 <i>В случае нарушения пользователем правил (отослал меньше средств, чем было заявлено), Вы в праве отменить заявку.
Отменять заявку без весомых аргументов карается штрафами или санкциями.</i>

⬜ Администратор <u>обязан</u> быть максимальное количество времени в сети для обработки заявок.</b>
""",
    "startMessageAdmin": """
<i><u>Здравствуй, Администратор</u></i>⚖️
Вас приветствует стартовое меню бота <b>Exchanger</b>💱
🔗 В случае вопросов пишите гл.администратору: @floix""",
    "startMessageUser": """<i><u>Здравствуйте</u></i>👋
Вас приветствует бот <b>Exchanger</b>💱
Выберите, каким способом Вы хотите произвести обмен💳
🔗 В случае вопросов пишите гл.администратору: @floix""",
    "profileTextUser": """<b>
⬇️ Ваш профиль ⬇️</b><i>
🆔 Ваш ID ⟶ <code>{userID}</code>
📇 KYC ⟶ <code>{KYCStatus}</code>
🕜 Зарегистрирован ⟶ <code>{dateRegistration}</code></i>
""",
    "statisticTextUser": """⬇️ Ваша статистика ⬇️
<i>💱 Всего сделок ⟶ <code>{countTransaction}</code></i>
<b>Количество:</b>
<i>    • 🕜 Сделок в статусу <b>WAIT</b> ⟶ <code>{WAIT}</code>
    • 📝 Сделок в статусу <b>ACCEPTED</b> ⟶ <code>{ACCEPTED}</code>
    • ✅ Сделок в статусу <b>COMPLETED</b> ⟶ <code>{COMPLETED}</code>
Сумма <u>завершенных</u> сделок ⟶ <code>{totalAmount} ₽</code>
Средняя сумма <u>завершенных</u> сделок ⟶ <code>{averageAmount} ₽</code>
💠 Любимая категория ⟶ <code>{typeTransaction}</code></i>
""",
    "missionsTextUser": "<b>🔶 Выберите одно из трех состояний заявки для получения информации "
    "относительно данной категории заявок.</b>",
    "missionsText": "<b>🔶 Выберите одно из трех состояний заявки для получения информации "
    "относительно данной категории заявок.</b>\n"
    "{missionsCount}",
    "informationMissions": "Для того, чтобы получить информацию о заявке - <b><i>нажмите</i></b> на нее.",
    "choiceToken": "Выберите <b><i>{typeWallet}</i></b> для осуществления {typeTransaction} средств 🪙",
    "getAddressCrypto": """Введите {typeTransaction}.
Если хотите вернуться обратно - нажмите "Назад".
Если хотите <b><i>отменить</i></b> обмен можете ввести или нажать /cancel""",
    "checkCorrectAddress": """🟢 Ваши данные:
<b><i>🛰️ Сеть</i></b> ⟶ <code>{net}</code>
<b><i>💳 Адрес кошелька</i></b> ⟶ <code>{wallet_address}</code>
🔶 Вы уверены, что это тот кошелек?""",
    "choiceMethod": """⚙️ Выберете удобный способ ввода суммы средств для перевода
или нажмите <b><i>"Отменить"</i></b> для отмены обмена.""",
    "settingsText": """💼 Администраторов в сети: <code>{adminsWork}</code>
🗃️ Ваш статус работы: <code>{workType}</code>,
💳 Количество кошельков в базе: <code>{countWallets}</code>
📇 Количество заявок в состоянии <b><i>WAIT</i></b>: <code>{countMissions}</code>
""",
    "walletsMenu": "Вы открыли меню рабочих кошельков.\n"
    "Здесь Вы можете <b><i>добавить</i></b> кошелек или, нажав на одну из позиций, "
    "<b><i>изменить данные</i></b> кошелька или <b><i>удалить</i></b> его.\n"
    "⚙️ <i>Изменить можно</i>:\n"
    "<b>･ <i>Статус (рабочий или нет)</i></b>\n"
    "<b>･ <i>Процент наценки ⚖️</i></b>\n"
    "<b>･ <i>Реквизиты 💳</i></b>\n"
    "<b>･ <i>Тип (Fiat 💸 | Crypto 🪙)</i></b>\n",
    "addWallet": "🔶 Введите <b><u>короткое</u></b> название <b><i>валюты</i></b>",
    "getNameNet": "🔶 Введите <b><i>реквизиты</i></b>",
    "getWalletType": "🔶 Выберите <b><i>тип кошелька</i></b>",
    "checkDataAddWallet": """Данные, которые Вы ввели:
🛰️ Валюта кошелька: <code>{nameNet}</code>
💳 Реквизиты кошелька: <code>{address}</code>
🗃️ Тип кошелька: <code>{walletType}</code>
Вы <b><i><u>уверены</u></i></b>, что это <b><i><u>верные</u></i></b> данные?
""",
    "addressMenu": "⬇️ <b><i>Выберите действие, которое хотите осуществить с данным кошельком</i></b> ⬇️",
    "sureDelete": "🔶 Вы уверены, что хотите удалить кошелек?",
    "deleteAddress": "Вы успешно удалили кошелек <code>{wallet}</code>!",
    "addressEdit": """📑 <b><i>Информация по кошельку</i></b>:
💳 Реквизиты ⟶ <code>{address}</code>
💼 Состояние кошелька ⟶ <code>{workType}</code>
⚖️ Процент наценки ⟶ <code>{percent}</code>""",
    "getPercent": "🔶 Вы уверены, что это верный процент - <code>{percent}</code>?",
    "percentEdit": "📝 Напишите процент, который будет стоять на этом кошельке в виде комиссии",
    "completedEditPercent": """🟢 Процент успешно сохранен! ✅
<b><i>Новый процент</i></b>: <code>{percent}</code>""",
    "getSum": """Напишите сумму перевода, который хотите совершить для обмена.
💳 <i>Минимальный ввод</i>: <code>{min_sum}</code> <i><b>{currency_from}</b></i>
⚖️ Курс <i><b>1 {currency_to}</b></i> ⟶ <code>{currency_rate}</code> <i><b>{currency_from}</b></i>""",
    "getSumCrypto": """Напишите сумму перевода, который хотите совершить для обмена.
💳 <i>Минимальный ввод</i>: <code>{min_sum}</code> <i><b>{currency_from}</b></i>
⚖️ Курс <i><b>1 {currency_to}</b></i> ⟶ <code>{currency_rate}</code> <i><b>{currency_from}</b></i>
📊 Комиссия сети ⟶ <code>{commission}</code> <b><i>{currency_to}</i></b>""",
    "checkTheCorrectTransaction": """📝 <b>Данные по сделки:</b>
<b><i>💱 Валюта в которой придут деньги:</i></b> <code>{name_net}</code>
<b><i>🪪 Кошелек куда придут деньги:</i></b> <code>{address}</code>
<b><i>💳 Сумма к оплате:</i></b> <code>{amount_from} {currency_from}</code>
<b><i>💸 Сумма к получению:</i></b> <code>{amount_to} {currency_to}</code>
<u><i><b>🔶 Все верно?</b></i></u>
""",
    "receiptVerification": """💼 <i>Для получения <code>{amount_to}</code> <b>{currency_to}</b>
📨 Переведите <code>{amount_from}</code> <b>{type_transaction}</b>
💳 На эти реквизиты ⟶ <code>{work_wallet}</code></i>

<b>                     📌 <u>ВНИМАНИЕ</u> 📌

🖍️ <u><i>НЕ УДАЛЯЙТЕ</i></u> это сообщение!
📜 Для того, чтобы Ваша заявка вступила в силу ⬇️
･ <u><i>ОБЯЗАТЕЛЬНО, после</i></u> отправки средств надо нажать на кнопку "Отправил ✅".
</b>""",
    "createMission": """<i>Вы успешно создали заявку на обмен!</i>
<b>⬇️ Данные по сделке ⬇️
📝 <i>Номер сделки</i> ⟶ <code>#{mission_id}</code>
💳 <i>Реквизиты куда придут средства</i> ⟶ <code>{user_requisites}</code>
💸 <i>Сумма средств, подлежащая зачислению на Ваш кошелек</i> ⟶ <code>{amount} {currency_to}</code></b>
""",
    "sendMission": """‼️ Заявка на обмен <b><i>{currencyTo}</i></b> ‼️
🔷 Номер заявки ⟶ <code>#{missionID}</code>
🆔 UserID ⟶ <code>{userID}</code>
🆔 AdminID ⟶ <code>{adminID}</code>
📥 Куда пришли средства от пользователя ⟶ <code>{workWallet}</code>
💳 Реквизиты пользователя ⟶ <code>{userRequisites}</code>
💵 Сумма средств, на зачисление <b><i>Администратору</i></b> ⟶ <code>{amountFrom}</code> <b>{walletCurrency}</b>
💶 Сумма средств, на зачисление <b><i>Пользователю</i></b> ⟶ <code>{amountTo}</code> <b>{currencyTo}</b>
⚜️ Статус заявки ⟶ <code>{statusMission}</code>
🕰️ Дата оформления заявки ⟶ <code>{dataTime}</code>
""",
    "sureRevoke": "🔶 Вы уверены, что хотите удалить заявку <code>#{missionID}</code>?",
    "changeStatus": "🟣 Нынешний статус заявки <code>#{missionID}</code> ⟶ <i><b>{statusMission}</b></i>",
    "changeStatusUser": "🟦 Ваша заявка <code>#{missionID}</code> сменила статус на <b><i>{statusMission}</i></b>",
    "informationMissionUser": """Информация по заявке <code>#{missionID}</code>
🆔 AdminID ⟶ <code>{adminID}</code>
📥 Ваши реквизиты ⟶ <code>{userRequisites}</code>
💳 Реквизиты Администратора ⟶ <code>{workWallet}</code>
💵 Сумма средств, на зачисление <b><i>Администратору</i></b> ⟶ <code>{amountFrom}</code> <b>{NameNet}</b>
💶 Сумма средств, на зачисление <b><i>Вам</i></b> ⟶ <code>{amountTo}</code> <b>{currencyTo}</b>
⚜️ Статус заявки ⟶ <code>{statusMission}</code>
🕰️ Дата оформления заявки ⟶ <code>{dataTime}</code>
""",
    "sureRevokeWithMessage": """🔶 Вы уверены, что хотите удалить заявку <code>#{missionID}</code>?
Сообщение Пользователю ⟶ <b><i>{messageRevoke}</i></b>""",
    "revokeSimpleA": "✅ Заявка успешно отменена!",
    "revokeWithTextA": "✅ Заявка успешно отменена!\nСообщение пользователю ⟶ <b><i>{messageRevoke}</i></b>",
    "revokeSimpleU": "❌ Ваша заявка <code>#{missionID}</code> отменена Администратором!",
    "revokeWithTextU": "❌ Ваша заявка <code>#{missionID}</code> отменена Администратором!\n"
    "Сообщение от Администратора ⟶ <b><i>{messageRevoke}</i></b>",
    "getMessageToRevoke": "<b>🟣 Введите сообщение, которое будет отправлено Пользователю.</b>",
    "deleteMissionUser": "✅ Вы успешно удалили заявку #{missionID}!",
    "verif": "⚠️ <i>Для верификации отправьте фотографию листочка, на котором будет написано <b>#{verifNumber}</b>,"
    " и карты на фоне</i> ⚠️\n\n⬆️ <i>Пример фотографии для верификации</i> ⬆️",
    "sendVerifPhoto": "<i>💾 Фотография успешно отправлена Администратору. Ожидайте вердикта верификации.</i>",
    "sendVerifPhotoAdmin": "<i><b>🟣 Поступила заявка</b> на верифицирование пользователя с ID <code>{userID}</code>\n\n"
    "🪪 Его выпавший номер <code>#{verifNumber}</code></i>",
    "approveVerif": "<i>✅ Пользователь с айди <code>{userID}</code> - успешно прошел верификацию!</i>",
    "approveVerifUser": "<i><b>✅ Вы успешно прошли верификацию!</b></i>",
    "rejectVerifAdmin": "<i>🚫 Вы отменили заявку на верификацию у пользователя с ID <code>{userID}</code>!</i> 🚫",
    "rejectVerifUser": "<i>‼️ Ваша заявка на верификацию отменена‼️\n\n<b>В случае не согласия с вердиктом,"
    " пишите администратору - @floix</b></i>",
    "statisticAdmin": """📊 <b>Статистика по боту @{botName}</b>
<b>💾 Новых пользователей за:</b>
<i>    • <u>Сегодня</u> ⟶ <code>{newUserToDay}</code>
    • <u>Неделю</u> ⟶ <code>{newUserToWeek}</code>
    • <u>Месяц</u> ⟶ <code>{newUserToMonth}</code>
    • <u>Все время</u> ⟶ <code>{UserTotal}</code></i>

<b>Количество пользователей совершивших обмен: {countExchangeUser}</b>

<b>💱 Обменов за:</b>
<i>    • <u>День</u> ⟶ <code>{exchangeToDay}</code>
    • <u>Неделю</u> ⟶ <code>{exchangeToWeek}</code>
    • <u>Месяц</u> ⟶ <code>{exchangeToMonth}</code>
    • <u>Все время</u> ⟶ <code>{exchangeTotal}</code></i>

<b>💸 Выручка за:</b>
<i>    • <u>Сегодня</u> ⟶ <code>{gainToDay}</code> ₽
    • <u>Неделю</u> ⟶ <code>{gainToWeek}</code> ₽
    • <u>Месяц</u> ⟶ <code>{gainToMonth}</code> ₽
    • <u>Все время</u> ⟶ <code>{gainTotal}</code></i> ₽


<b>💰 Самый крупный обмен за все время:</b>
<i>    • 💷 <u>Сумма</u> ⟶ <code>{maxExchangeAmount}</code> ₽
    • 🆔 <u>UserID</u> ⟶ <code>{maxExchangeUserID}</code>
    • 📆 <u>Время</u> ⟶ <code>{maxExchangeDateTime}</code></i>

<b>🗃️ Работник месяца:</b>
<i>    • 🆔 <u>UserID</u> ⟶ <code>{topWorker}</code></i>

<b>🆔 UserID человека, который совершил обмен большое количество раз ⟶ <code>{topExchangerUserID}</code>

⚜️ Самое популярное направление на обмен ⟶ <code>{topTypeExchange}</code>
🔱 Самая популярная валюта на обмен ⟶ <code>{topTypeCurrency}</code></b>
""",
    "editPatterns": "<b><i>Вы можете добавить новый токен и паттнер к нему или, нажав на паттерн, "
    "удалить его.</i></b>\n\n{patterns}",
    "deletePatterns": "<b><i>✅ Вы успешно удалили паттерн <code>{deletePattern}</code>.</i></b>\n\n{patterns}",
    "getTokenPattern": "<b><i>🔶 Введите короткое название валюты для этого паттнера.</i></b>",
    "getPattern": "<b><i>🔶 Введите паттерн для этой валюты - <code>{token}</code></i></b>",
    "sureAddedPattern": "<b><i>🔶 Вы уверены, что хотите добавить <code>{token}</code> -"
    " <code>{pattern}</code>?</i></b>",
    "addPatterns": "<b><i>✅ Вы успешно добавили новый паттнер!</i></b>\n\n{patterns}",
    "editMinSum": "<b><i>🔶 Введите сумму в рублях.</i></b>",
    "sureUpdateMinSum": "<b><i>🔶 Вы уверены, что хотите обновить минимальную сумму "
    "перевода средств на <code>{minSum}</code></i></b>",
    "updateMinSum": "<b><i>✅ Вы успешно обновили минимальную сумму ввода!\nНовая minimalSum ⟶"
    " <code>{updateMinSum}</code></i></b>",
}

errorLexicon: dict[str:str] = {
    "errorAddress": """🔴 <b>Вы ввели неверный адрес кошелька</b> 🔴
<b><i>🛰️ Сеть</i></b> ⟶ <code>{net}</code>
<b><i>💳 Адрес кошелька</i></b> ⟶ <code>{wallet_address}</code>""",
    "errorToken": """🔴 <b>Вы ввели неверное название валюты</b> 🔴
В случае, если Вы <b><i>уверены</i></b>, что введенная Вами валюта существует — напишите администратору @floix
<b><i>🛰️ Сеть</i></b> ⟶ <code>{net}</code>""",
    "WalletExist": """🔴 <b>Кошелек с такими данными уже <i><u>существуют</u></i></b> 🔴
🛰️ Валюта кошелька: <code>{nameNet}</code>
💳 Реквизиты кошелька: <code>{address}</code>
🗃️ Тип кошелька: <code>{walletType}</code>""",
    "IsDigitPercent": """🔴 <b>ОШИБКА</b> 🔴
Неверное сообщение! Не является числом или не попало в интервал от 1 до 1.7 - <code>{digit}</code>""",
    "getSum_minimal": """🔴 <b>ОШИБКА</b> 🔴
<code>{amount}</code> <b>{currency_from}</b> - меньше допустимого значения.""",
    "anotherAdminTakeMiss": """🔴 <b>ОШИБКА</b> 🔴
<i>Другой администратор уже взял эту заявку!</i>""",
    "errorMission": """<b>🔴 <b>ОШИБКА</b> 🔴
<i>В этой категории нет еще заявок!</i></b>""",
    "errorKYC": """<b>⚠️ ОШИБКА ⚠️
<i>Для того, чтобы переводить деньги на карту надо пройти KYC</i>‼️</b>""",
    "errorSendVerifPhoto": "⚠️ <b><i>{contentType}</i></b> ← не является Photo ⚠️\n\nНапоминаем, чтобы пройти"
    " верификацию <i><u>необходимо отправить "
    "фотографию листочком с номером</u>‼️ <code>#{numberVerif}</code> ‼️"
    " <u>и картой на фоне!</u></i>",
    "repeatPattern": """<b>🔴 <b>ОШИБКА</b> 🔴
<i>Такой паттерн уже существует!\n<b><i>Удалите нынешний и добавьте новый!</i></b>""",
    "IsDigitMinSum": """🔴 <b>ОШИБКА</b> 🔴
Неверное сообщени! Не ялвяется числом - <code>{digit}</code>"""
}

startCallbackUser: dict[str:str] = {
    "rub-crypto": "RUB 💸 ⟶ CRYPTO ₿",
    "crypto-rub": "CRYPTO ₿ ⟶ RUB 💸",
    "crypto-crypto": "CRYPTO ₿ ⟶ CRYPTO ₿",
    "info": "Информация 📒",
    "profile": "Профиль 🪪",
}

startCallbackAdmin: dict[str:str] = {
    "statistics": "Статистика 📊",
    "information": "Информация 📒",
    "instruction": "Инструкция 📎",
    "settings": "Настройки ⚙️",
}

checkMark: dict[str:str] = {"yes": "✅"}

yesLexicon: dict[str:str] = {"yes": "Да ✅"}

addLexicon: dict[str:str] = {"add": "Добавить 💾"}

profileUser: dict[str:str] = {"missions": "Заявки 📨", "statistics": "Статистика 📊"}

repeatLexicon: dict[str:str] = {"repeat": "Повторить ввод 🔁"}

listMissions: dict[str:str] = {
    "wait": "В ожидание 🕜",
    "accepted": "Принятые 📝",
    "completed": "Завершенные ✅",
}

choiceToken: dict[str:str] = {"btc": "BTC 💳", "eth": "ETH 💳"}

checkCorrectAddress: dict[str:dict] = {
    "choiceGetSum": yesLexicon["yes"],
    "no": "Нет ❌",
}

repeatAddress: dict[str:str] = {"repeat": "Повторить 🔁"}

choiceMethod: dict[str:str] = {
    "crypto": "CRYPTO ₿",
    "rub": "🇷🇺 RUB ₽",
    "usd": "🇺🇸 USD $",
}

settingsMenu: dict[str:str] = {
    "workType": None,
    "wallets": "Кошельки 💼",
    "editMinSum": "Edit minSum 💵",
    "editPatterns": "Изменить паттерны 📎",
}

workType: dict[bool:str] = {True: "Работаю ✅", False: "Не работаю ❌"}

missions: dict[str:str] = {"missions": "Заявки 📑"}

walletsMenu: dict[str:str] = {"addWallet": addLexicon["add"]}

patternsMenu: dict[str:str] = {"addPattern": addLexicon["add"]}

walletType = {"rub": "RUB 💳", "crypto": "CRYPTO 🪙"}

checkCorrectAddWallet: dict[str:dict] = {
    "yes": yesLexicon["yes"],
    "no": repeatLexicon["repeat"],
}

successfullyMessage: dict[str:str] = {
    "addWallet": """✅ Кошелек <b><i>добавлен</i></b> в базу данных ✅
<i>Информация по нему</i>:
🛰️ Валюта кошелька: <code>{nameNet}</code>
💳 Реквизиты кошелька: <code>{address}</code>
🗃️ Тип кошелька: <code>{walletType}</code>
"""
}

addressMenu: dict[str:str] = {
    "deleteAddress": "Удалить кошелек ❌",
    "addressEdit": "Изменить данные 🪪",
}

sureLexicon: dict[str:str] = {"yes": yesLexicon["yes"], "no": "Отменить ❌"}

addressDelete: dict[str:str] = {"wallets": "Кошельки 📒"}

addressEdit: dict[str:str] = {"statusWork": "", "percentEdit": "Изменить процент ⚖️"}

statusWork: dict[str:str] = {True: "Работает ✅", False: "Не работает ❌"}

backLexicon: dict[str:str] = {
    "cancelLexicon": "Отменить 🔚",
    "backLexicon": "Вернуться 🔚",
    "backMainMenu": "Главное меню 🔚",
    "backMission": "Вернуться к заявкам 🔚",
}

repeatGetPercent: dict[str:str] = {"repeatGetPercent": repeatLexicon["repeat"]}

checkPercent: dict[str:str] = {"checkPercent": yesLexicon["yes"]}

cryptoSymbol: dict[str:str] = {"symbol": "🪙"}

minSum: dict[str:str] = {"minSum": "💱 Минимальная сумма"}

getSum: dict[str:str] = {
    "getSum": yesLexicon["yes"],
    "repeatGetSum": repeatLexicon["repeat"],
}

receiptVerification: dict[str:str] = {"sent": "Отправил ✅"}

repeatGetSum: dict[str:str] = {"repeatGetSum": repeatLexicon["repeat"]}

fiatOrCrypto: dict[str:str] = {
    "RUB": "способ оплаты (RUB - карта)",
    "CRYPTO": "криптовалюту",
}

writeFiatOrCrypto: dict[str:str] = {
    "CRYPTO": "адрес Вашего <b><i>криптокошелька</i></b>",
    "RUB": "Ваши <b><i>реквизиты</i></b>",
}

writeGetOrSend: dict[str:str] = {
    "GET": "перевода",
    "SEND": "получения",
    "TRANSLATE": "ввода",
}

sendMission: dict[str:str] = {
    "changeStatus": "Изменить статус 📌",
}

revokeButton: dict[str:str] = {
    "revoke": "Отменить заявку 🚫",
    "revokeWithMessage": "Отменить с сообщением ⚠️",
}

changeStatus: dict[str:str] = {
    "wait": "wait 🕜",
    "accepted": "accepted 📝",
    "completed": "completed 🏷️",
}

informationMissionUser: dict[str:str] = {"information": "📜 Информация"}

revokeMission: dict[str:str] = {"YesRevokeMission": yesLexicon["yes"]}

kycVerificationLexicon: dict[str:str] = {True: "Verified 🟢", False: "Not verified 🔴"}

kycVerify: dict[str:str] = {"verify": "Пройти верификацию ✅"}

kycVerifyCheckAdmin: dict[str:str] = {
    "verifUser": "Одобрить ✅",
    "reject": "Отклонить 🚫",
}
