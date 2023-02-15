# Telegram_Imaginarium_bot
Телеграмм бот для настольной игры Имаджинариум

Главная задача бота раздавать карты для игры Имаджинариум.

Требования:
Вся компания должна физически находиться рядом.
Вы должны быть ознакомлены с игрой Имаджинариум и её правилами.
Бот лишь выдает карточки игрокам, но не заменяет всю игру целиком.
Для игры нужны поле, фигуры игроков, номерки для голосования (при желании необязательно иметь оригинальную игру, можно самим нарисовать поле, подобие фигур игроков и номерки))))

Как это работает:
Главный игрок создает комнату в боте, делает первичные настройки игры.
Бот формирует комнату и отдает ее номер.
Другие игроки подключаются к данной комнате.
Когда комната будет заполнена главный игрок сможет раздать карты.
Бот разошлет всем игрокам карточки первой раздачи.
Ведущий игрок раунда придумывает ассоциацию к одной из 6ти имеющихся у него карточек, говорит игрокам ассоциацию вслух, выбирает в меню бота номер выбранной карты.
Игроки выбирают свои карточки в соответствии с ассоциацией ведущего и делают выбор номера своей карточки в боте.
Когда все игроки сделали свой выбор - бот автоматически присылает каждому игроку одну из выбранных всеми игроками карт (карты присылаются рандомно, это может быть как ваша карта, так и чужая).
Игроки выкладывают телефоны с присланной карточкой на стол.
Происходит голосование, подсчет очков, ходы по полю.
Командой "Старт игры" объявляется новый раунд, бот заменяет использованные карточки и присылает новый набор из 6ти карточек каждому игроку.
