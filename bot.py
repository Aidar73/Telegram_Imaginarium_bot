import os
import random
import telebot
from dotenv import load_dotenv
from telebot import types


load_dotenv()

token = os.getenv('TELEGRAM_TOKEN')

bot = telebot.TeleBot(token)


# Функция для обработки команды /start
@bot.message_handler(commands=['start'])
def start(message):
    buttons = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton('Новая игра', callback_data='new_game')
    button2 = types.InlineKeyboardButton('Присоединиться', callback_data='join_game')
    button3 = types.InlineKeyboardButton('Завершить игру', callback_data='end_game')
    button4 = types.InlineKeyboardButton('Об игре', callback_data='help')
    buttons.add(button1, button2, button3, button4)
    bot.send_message(message.chat.id, text='Добро пожаловать в игру Имаджинариум! Вы можете играть вместе с другими людьми, нажимая на кнопки ниже', reply_markup=buttons)


# Создаем пустой словарь для хранения игровых комнат
rooms = {}


# Функция для обработки нажатия кнопок меню /start
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message:
        if call.data == 'new_game':
            if call.from_user.id in rooms:
                bot.send_message(call.from_user.id, f'Ваша игровая комната уже создана! Для её завершения введите /endgame')
            else:
                new_game(call.from_user.id)
        elif call.data == 'join_game':
            if not rooms:
                bot.send_message(call.message.chat.id, text='Нет игровых комнат /start')
            else:
                room_id = bot.send_message(call.message.chat.id, 'Введите код комнаты:')
                bot.register_next_step_handler(room_id, join_game)
        elif call.data == 'end_game':
            end_game(call.from_user.id)
        elif call.data == 'help':
            welcome_help(call.message)


# Функция для создания новой игровой комнаты
@bot.message_handler(commands=['newgame'])
def new_game(message):
    # Создаем новую игровую комнату
    room_id = message
    rooms[room_id] = {
        'card_all': [int(i) for i in range(1, 85)],
        'card_use': [],
        'card_free': [],
        'players': {message: []}
    }
    # Отправляем сообщение с информацией о комнате
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Старт игры")
    markup.add(btn1)
    bot.send_message(message,
                     text=f'Новая игра создана! Пригласите других игроков в эту игровую комнату. Код комнаты и пароль: {room_id}',
                     reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):
    if message.text == "Старт игры":
        start_game(message)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Обновить карточки")
        btn2 = types.KeyboardButton("Завершить игру")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, text="Выберите действие", reply_markup=markup)

    elif (message.text == "Обновить карточки"):
        update_cards(message.from_user.id)

    elif message.text == "Завершить игру":
        end_game(message.from_user.id)


# Функция для присоединения к игровой комнате
def join_game(message):
    # Получаем код комнаты из сообщения
    room_id = int(message.text)
    # Проверяем, существует ли комната
    if room_id in rooms:
        if message.from_user.id not in rooms[room_id]['players']:
            # Добавляем игрока в комнату
            rooms[room_id]['players'][message.from_user.id] = []
            # Отправляем сообщение с информацией о комнате
            bot.send_message(message.chat.id, f'Вы присоединились к игровой комнате. Код комнаты: {str(room_id)}')
            print(rooms)
        else:
            # Если игрок повторно пытается присоединиться к комнате
            bot.send_message(message.chat.id, f'Вы уже в игре!')
    else:
        # Отправляем сообщение об ошибке
        bot.send_message(message.chat.id, 'Комната не найдена!')


# Обработчик команды /endgame
@bot.message_handler(commands=['endgame'])
def end_game(message):
    # Получаем идентификатор игры
    room_id = message
    # Проверяем, существует ли такая игра
    if room_id in rooms:
        del rooms[room_id]
        # Отправляем сообщение с подтверждением
        bot.send_message(message, f'Игра {str(room_id)} завершена!')
    else:
        # Отправляем сообщение с ошибкой
        bot.send_message(message, 'Вы ещё не создавали или уже завершили свою игру.')


# Функция для начала игры
def start_game(message):
    # Получаем код комнаты из сообщения
    room_id = message.from_user.id
    # Проверяем, существует ли комната
    if room_id in rooms:
        # Получаем список игроков
        players = rooms[room_id]['players']
        # Отправляем игрокам 6 карточек с изображениями
        for player in players:
            bot.send_message(player, 'Начинаем игру! Вам отправлены 6 карточек.')
            for i in range(6):
                # Генерируем случайное изображение вырезая его из основного списка карточек
                card = rooms[room_id]['card_all'].pop(random.randint(0, len(rooms[room_id]['card_all'])))
                # Пополняем список использованных карточек
                rooms[room_id]['card_use'].append(card)
                # Добавляем карточку в список карточек комнаты
                rooms[room_id]['players'][player].append(card)
                # Отправляем изображение игроку
                bot.send_photo(player, open(f'img/{card}.jpg', 'rb'))
                # print(rooms[room_id]['card_all'])
                # print(rooms[room_id]['card_use'])
                # print(rooms[room_id]['players'])
    else:
        # Отправляем сообщение об ошибке
        bot.send_message(message.chat.id, 'Комната не найдена!')


# Функция для обновления карточек
def update_cards(message):
    # Получаем код комнаты из сообщения
    room_id = message
    # Проверяем, существует ли комната
    if room_id in rooms:



        card = user
        card = rooms[room_id]['card_use'].pop(card)
        rooms[room_id]['card_free'].append(card)




        # Получаем список игроков
        players = rooms[room_id]['players']
        # Получаем список карточек
        if len(rooms[room_id]['card_all']) < len(players):
            rooms[room_id]['card_all'] += rooms[room_id]['card_free']
            rooms[room_id]['card_free'] = []
        # Заменяем одну из карточек на новую

        # Отправляем изображение игрокам
        for player in players:
            bot.send_message(player, 'Одна из карточек была заменена!')
            for i in range(6):
                # Генерируем случайное изображение вырезая его из основного списка карточек
                card = rooms[room_id]['card_all'].pop(random.randint(0, len(rooms[room_id]['card_all'])))
                # Пополняем список использованных карточек
                rooms[room_id]['card_use'].append(card)
                # Добавляем карточку в список карточек комнаты
                rooms[room_id]['players'][player].append(card)
                # Отправляем изображение игроку
                bot.send_photo(player, open(f'img/{card}.jpg', 'rb'))

        # print(rooms[room_id]['card_all'])
        # print(rooms[room_id]['card_use'])
        # print(rooms[room_id]['players'])
    else:
        # Отправляем сообщение об ошибке
        bot.send_message(message.chat.id, 'Комната не найдена!')


@bot.message_handler(commands=['help'])
def welcome_help(message):
    text = '''Главная задача бота раздавать карты для игры Имаджинариум.

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
Ведущий игрок раунда выбирает карточку, говорит игрокам ассоциацию и выкладывает телефон с фото на стол.
Игроки выбирают свои карточки в соответствии с ассоциацией ведущего и также выкладывают телефоны на стол.
Происходит голосование, подсчет очков, ходы по полю.
С новым раундом бот заменяет использованные карточки.

Для перехода к главному меню всегда используйте команду /start'''
    message = bot.send_message(message.chat.id, text)


# Запускаем бота
if __name__ == '__main__':
    bot.polling(none_stop=True)









