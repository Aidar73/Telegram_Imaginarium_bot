import os
import random
import telebot
from dotenv import load_dotenv
from telebot import types


load_dotenv()

token = os.getenv('TELEGRAM_TOKEN')

bot = telebot.TeleBot(token)

# Создаем пустой словарь для хранения игровых комнат
rooms = {}

# Создаем пустой словарь для хранения игровых комнат игроков сервера
players_in_games = {}

# Функция для обработки команды /start
@bot.message_handler(commands=['start'])
def start(message):
    buttons = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton('Новая игра', callback_data='new_game')
    button2 = types.InlineKeyboardButton('Присоединиться', callback_data='join_game')
    button3 = types.InlineKeyboardButton('Завершить игру', callback_data='end_game')
    button4 = types.InlineKeyboardButton('Выйти из игры', callback_data='exit_game')
    button5 = types.InlineKeyboardButton('Об игре', callback_data='help')
    buttons.add(button1, button2, button3, button4, button5)
    bot.send_message(message.chat.id, text='Добро пожаловать в игру Имаджинариум! Вы можете играть вместе с другими людьми, нажимая на кнопки ниже', reply_markup=buttons)


# Функция для обработки нажатия кнопок меню /start
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message:
        if call.data == 'new_game':
            if call.from_user.id in rooms:
                bot.send_message(call.from_user.id, f'Ваша игровая комната уже создана! Для её завершения нажмите соответствующую кнопку /start, либо когда вся компания будет готова запустите игру командой "Старт игры"')
            elif call.from_user.id in players_in_games:
                bot.send_message(call.from_user.id, f'Вы ещё не вышли из игры {players_in_games[call.from_user.id]}! Для выхода из неё нажмите соответствующую кнопку /start')
            else:
                new_game(call.from_user.id)
        elif call.data == 'join_game':
            if not rooms:
                bot.send_message(call.message.chat.id, text='Нет игровых комнат. Создайте свою игру и играйте со своими друзьям /start')
            elif call.from_user.id in players_in_games:
                bot.send_message(call.from_user.id, f'Вы уже в игровой комнате {players_in_games[call.from_user.id]}! Для выхода из неё нажмите соответствующую кнопку /start')
            else:
                room_id = bot.send_message(call.message.chat.id, 'Введите код комнаты:')
                bot.register_next_step_handler(room_id, join_game)
        elif call.data == 'end_game':
            end_game(call.from_user.id)
        elif call.data == 'exit_game':
            exit_game(call.from_user.id)
        elif call.data == 'help':
            welcome_help(call.message)
        elif call.data.startswith('№'):
            round_card(call)



# Функция для создания новой игровой комнаты
@bot.message_handler(commands=['newgame'])
def new_game(message):
    # Создаем новую игровую комнату
    room_id = message
    rooms[room_id] = {
        'card_all': [int(i) for i in range(1, 85)],
        'card_users': [],
        'card_round': [],
        'players': {message: []}
    }
    # Добавляем игрока в список игроков сервера
    players_in_games[message] = room_id
    # Отправляем сообщение с информацией о комнате
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton("Старт игры")
    markup.add(btn1)
    bot.send_message(message,
                     text=f'Новая игра создана!\nПригласите других игроков в эту игровую комнату. Код комнаты: {room_id}.\nКогда вся компания будет готова запустите игру командой "Старт игры"',
                     reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):
    if message.text == "Старт игры":
        start_game(message)
    #     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    #     btn1 = types.KeyboardButton("Обновить карточки")
    #     btn2 = types.KeyboardButton("Завершить игру")
    #     markup.add(btn1, btn2)
    #     bot.send_message(message.chat.id, text="Вы ведущий и у Вас есть кнопки для", reply_markup=markup)
    #
    # elif message.text == "Обновить карточки":
    #     update_cards(message.from_user.id)
    #
    # elif message.text == "Завершить игру":
    #     end_game(message.from_user.id)


# Функция для присоединения к игровой комнате
def join_game(message):
    # Получаем код комнаты из сообщения
    room_id = int(message.text)
    # Проверяем, существует ли комната
    if room_id in rooms:
        if message.from_user.id not in rooms[room_id]['players']:
            # Добавляем игрока в комнату
            rooms[room_id]['players'][message.from_user.id] = []
            # Добавляем игрока в список игроков сервера
            players_in_games[message] = [room_id]
            # Отправляем сообщение с информацией о комнате
            bot.send_message(message.chat.id, f'Вы присоединились к игровой комнате. Код комнаты: {str(room_id)}.\nОжидайте начала игры')
        else:
            # Если игрок повторно пытается присоединиться к комнате
            bot.send_message(message.chat.id, f'Вы уже в игре!')
    else:
        # Отправляем сообщение об ошибке
        bot.send_message(message.chat.id, 'Комната не найдена!')


# Обработчик команды /exitgame
@bot.message_handler(commands=['exitgame'])
def exit_game(message):
    # Получаем идентификатор игрока
    player_id = int(message)
    # Проверяем, существует ли такая игра
    if player_id in rooms:
        bot.send_message(player_id, f'Вы хотите выйти из своей игры?\nДля выхода и завершения вашей игры нажмите соответствующую кнопку /start')
    elif player_id in players_in_games:
        room_id = players_in_games[player_id]
        del rooms['players'][player_id]
        del players_in_games[player_id]
        # Отправляем сообщение с подтверждением
        bot.send_message(message, f'Вы вышли из игровой конматы {str(room_id)}!\nСоздайте новую или присоединитесь к своим друзьям! /start')
    else:
        # Отправляем сообщение с ошибкой
        bot.send_message(message, 'Вы нигде не играете.')


# Обработчик команды /endgame
@bot.message_handler(commands=['endgame'])
def end_game(message):
    # Получаем идентификатор игры
    room_id = message
    # Проверяем, существует ли такая игра
    if room_id in rooms:
        del rooms[room_id]
        del players_in_games[message]
        # Отправляем сообщение с подтверждением
        bot.send_message(message, f'Игра {str(room_id)} завершена!\nСоздайте новую или присоединитесь к своим друзьям! /start')
    else:
        # Отправляем сообщение с ошибкой
        bot.send_message(message, 'Вы ещё не создавали или уже завершили свою игру.')


# Функция для начала игры
# @bot.message_handler(commands=['startgame'])
def start_game(message):
    if message.from_user.id not in players_in_games:
        bot.send_message(message.chat.id, text='Вы ещё не присоединились ни к одной из игр /start')
    else:
        # Получаем код комнаты из сообщения
        room_id = players_in_games[message.from_user.id]
        # Проверяем, существует ли комната
        if room_id in rooms:
            # Получаем список игроков
            players = rooms[room_id]['players']
            # Отправляем игрокам 6 карточек с изображениями
            for player in players:
                if not rooms[room_id]['players'][player]:
                    bot.send_message(player, 'Начинаем игру! Вам отправлены 6 карточек.')
                    # Формируем набор карточек для нового игрока и отправлем их
                    for i in range(6):
                        # Генерируем случайное изображение из основного списка карточек
                        card = random.choice(rooms[room_id]['card_all'])
                        # Удаляем выбранное изображение из основного списка карточек
                        rooms[room_id]['card_all'].remove(card)
                        # Пополняем список карточек пользователей на руках
                        rooms[room_id]['card_users'].append(card)
                        # Добавляем карточку в список карточек игрока
                        rooms[room_id]['players'][player].append(card)
                        # Отправляем изображение игроку
                        bot.send_photo(player, open(f'img/{card}.jpg', 'rb'), caption=f'{card}')
                        # print(rooms[room_id]['card_all'])
                        # print(rooms[room_id]['card_use'])
                        # print(rooms[room_id]['players'])
                    buttons = types.InlineKeyboardMarkup(row_width=3)
                    for i in rooms[room_id]['players'][player]:
                        buttons.add(types.InlineKeyboardButton(f'{i}', callback_data=f'№ {i}'))
                    bot.send_message(player,
                                     text=f'Ведущий загадывает карточку и называет ассоциацию.\nКаждый игрок (в том числе и ведущий) должен выбрать карточку в соответсвии с названной ассоциацией.\nВыбранные карточки будут разосланы игрокам рандомным образом, после эти карточки будут заменены на новые',
                                     reply_markup=buttons)
                else:
                    # Генерируем случайное изображение из основного списка карточек
                    card = random.choice(rooms[room_id]['card_all'])
                    # Удаляем выбранное изображение из основного списка карточек
                    rooms[room_id]['card_all'].remove(card)
                    # Пополняем список карточек пользователей на руках
                    rooms[room_id]['card_users'].append(card)
                    # Добавляем карточку в список карточек игрока
                    rooms[room_id]['players'][player].append(card)
                    bot.send_message(player, 'Новый раунд! Вам отправлены 6 карточек.')
                    # Отправляем игрокам 6 карточек с изображениями а также делаем кнопки
                    buttons = types.InlineKeyboardMarkup(row_width=3)
                    for card in rooms[room_id]['players'][player]:
                        # Отправляем изображение игроку
                        bot.send_photo(player, open(f'img/{card}.jpg', 'rb'), caption=f'{card}')
                        buttons.add(types.InlineKeyboardButton(f'{card}', callback_data=f'№ {card}'))
                    bot.send_message(player,
                                     text=f'Ведущий загадывает карточку и называет ассоциацию.\nКаждый игрок (в том числе и ведущий) должен выбрать карточку в соответсвии с названной ассоциацией.\nВыбранные карточки будут разосланы игрокам рандомным образом, после эти карточки будут заменены на новые',
                                     reply_markup=buttons)
        else:
            # Отправляем сообщение об ошибке
            bot.send_message(message.chat.id, 'Комната не найдена!')


def round_card(message):
    if message.from_user.id not in players_in_games:
        bot.send_message(message.from_user.id, text='Вы ещё не присоединились ни к одной из игр /start')
    else:
        # bot.delete_message(call.message.chat.id, call.message.message_id)
        # Получаем код комнаты из сообщения
        room_id = players_in_games[message.from_user.id]
        # Получаем номер выбранной карточки игрока
        card_choice = int(message.data.split()[1])
        # Добавляем карту в список карт раунда
        rooms[room_id]['card_round'].append(card_choice)
        # Удаляем эту карту из списка карт всех игроков, а также у игрока
        rooms[room_id]['card_users'].remove(card_choice)
        rooms[room_id]['players'][message.from_user.id].remove(card_choice)
        # Получаем список игроков
        players = rooms[room_id]['players']
        if len(rooms[room_id]['card_round']) == len(players):
            # for player in players:
                # markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                # for i in player.values():
                #     btn = types.KeyboardButton(f'/№ {i}')
                #     markup.add(btn)
                # bot.send_message(player,
                #                  text=f'Игроки сделали свой выбор.\nГолосуем!',
                #                  reply_markup=markup)

            # Отправляем игрокам по 1 карточке с изображениями, которые выбирали игроки
            for player in players:
                # Генерируем случайное изображение из списка карточек раунда
                card = random.choice(rooms[room_id]['card_round'])
                # Удаляем выбранное изображение из списка карточек раунда
                rooms[room_id]['card_round'].remove(card_choice)
                # Пополняем основной список карт освободившейся карточкой
                rooms[room_id]['card_all'].append(card)
                # Отправляем случайное изображение каждому игроку
                bot.send_photo(player, open(f'img/{card}.jpg', 'rb'), caption=f'№ {card}')
                bot.send_message(player, f'Все игроки выбрали по карточке, Вам отправлена одна из выбранных карточек с её номером. \nМожно выложить телефоны с присланной Вам карточкой на стол и голосуем! После голосования обновляем карточки командой "Старт игры"')


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









