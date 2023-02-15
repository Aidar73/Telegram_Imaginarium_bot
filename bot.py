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
    # Главное меню
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
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=f"Вы выбрали фото {call.data}!")
            round_card(call)


# Функция для обработки ввода сообщений
@bot.message_handler(content_types=['text'])
def func(message):
    if message.text == "Старт игры":
        start_game(message)
    if message.text == "Меню":
        start(message)


# Функция для создания новой игровой комнаты
@bot.message_handler(commands=['newgame'])
def new_game(message):
    # Создаем новую игровую комнату
    room_id = message
    rooms[room_id] = {
        'card_all': [int(i) for i in range(1, 477)],
        'card_users': [],
        'card_round': [],
        'players': {message: []}
    }
    # Добавляем игрока в список игроков сервера
    players_in_games[message] = room_id
    # Отправляем сообщение с информацией о комнате
    bot.send_message(message, f'Новая игра создана!\nПригласите других игроков в эту игровую комнату. Код комнаты: {room_id}.\nКогда вся компания будет готова запустите игру командой "Старт игры"')
    # Кнопки меню и старта игры
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    btn1 = types.KeyboardButton("Старт игры")
    btn2 = types.KeyboardButton("Меню")
    markup.add(btn1, btn2)
    bot.send_message(message,
                     text=f'Кнопка "Старт игры" запускает игру и новые раунды.\nКнопка "Меню" для вызова главного меню, также как и команда /start',
                     reply_markup=markup)


# Функция для присоединения к игровой комнате
def join_game(message):
    # Получаем код комнаты из сообщения
    room_id = int(message.text)
    # Проверяем, существует ли комната
    if room_id in rooms:
        if message.from_user.id not in rooms[room_id]['players']:
            # Проверяем, не начилась ли уже игра
            len_card_users = [len(rooms[room_id]['players'][player]) for player in rooms[room_id]['players']]
            if all([i == 0 for i in len_card_users]):
                # Отправляем игрокам комнаты уведомление, что к нам присоединился новый игрок
                for player in rooms[room_id]['players']:
                    bot.send_message(player, f'К нам присоединился новый игрок @{message.from_user.username}.')
                # Добавляем игрока в комнату
                rooms[room_id]['players'][message.from_user.id] = []
                # Добавляем игрока в список игроков сервера
                players_in_games[message.from_user.id] = room_id
                # Отправляем сообщение с информацией о комнате
                bot.send_message(message.chat.id, f'Вы присоединились к игровой комнате. Код комнаты: {str(room_id)}.\nОжидайте начала игры')
                # Кнопки меню и старта игры
                markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
                markup.add(types.KeyboardButton("Меню"))
                bot.send_message(message.chat.id,
                                 text=f'Кнопка "Меню" для вызова главного меню, также как и команда /start',
                                 reply_markup=markup)
            else:
                bot.send_message(message.chat.id, f'Игра уже началась и войти не получится!\nПересоздайте игру или поищите другую комнату. /start')
        else:
            # Если игрок повторно пытается присоединиться к комнате
            bot.send_message(message.chat.id, f'Вы уже в игре!')
    else:
        # Отправляем сообщение об ошибке
        bot.send_message(message.chat.id, 'Комната не найдена!')


# Обработчик команды выхода из комнаты/exitgame
@bot.message_handler(commands=['exitgame'])
def exit_game(message):
    # Получаем идентификатор игрока
    player_id = int(message)
    # Проверяем, существует ли такая игра
    if player_id in rooms:
        bot.send_message(player_id, f'Вы хотите выйти из своей игры?\nДля выхода и завершения вашей игры нажмите соответствующую кнопку /start')
    elif player_id in players_in_games:
        room_id = players_in_games[player_id]
        # Пополняем основной список карт освободившимися карточками
        for card in rooms[room_id][player_id]:
            rooms[room_id]['card_all'].append(card)
            rooms[room_id]['card_users'].remove(card)
        del rooms[room_id]['players'][player_id]
        del players_in_games[player_id]
        # Отправляем игрокам комнаты уведомление, что к нам присоединился новый игрок
        for player in rooms[players_in_games[player_id]]['players']:
            bot.send_message(player, f'@{message.from_user.username} вышел из игры.')
        # Отправляем сообщение с подтверждением
        bot.send_message(message, f'Вы вышли из игровой конматы {str(room_id)}!\nСоздайте новую или присоединитесь к своим друзьям! /start')
    else:
        # Отправляем сообщение с ошибкой
        bot.send_message(message, 'Вы нигде не играете.')


# Обработчик команды завершения игры и закрытия комнаты /endgame
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
        bot.send_message(message, 'Вы пытаетесь завершить не свою игру, ещё не создавали или уже завершили свою игру.')


# Функция для начала игры
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
            # Условие: ни у кого нет карточек (начало игры) или у всех 5, то можно начинать новую раздачу
            len_card_users = [len(rooms[room_id]['players'][player]) for player in players]
            if all([i == 0 for i in len_card_users]):
                # Отправляем игрокам 6 карточек с изображениями
                for player in players:
                    if not rooms[room_id]['players'][player]:
                        bot.send_message(player, 'Начинаем игру! Вам отправлены 6 карточек.')
                        buttons = types.InlineKeyboardMarkup(row_width=3)
                        imgs = []
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
                            imgs.append(telebot.types.InputMediaPhoto(open(f'img/{card}.jpg', 'rb'), caption=f'{card}'))
                            # bot.send_photo(player, open(f'img/{card}.jpg', 'rb'), caption=f'{card}')
                            buttons.add(types.InlineKeyboardButton(f'{card}', callback_data=f'№ {card}'))
                        bot.send_media_group(player, imgs)
                        bot.send_message(player,
                                         text=f'Ведущий загадывает карточку и называет ассоциацию.\nКаждый игрок (в том числе и ведущий) должен выбрать № карточки в соответсвии с названной ассоциацией (№ карточки в описании каждого фото).',
                                         reply_markup=buttons)
            elif all([i == 5 for i in len_card_users]):
                for player in players:
                    # Генерируем случайное изображение из основного списка карточек
                    card = random.choice(rooms[room_id]['card_all'])
                    # Удаляем выбранное изображение из основного списка карточек
                    rooms[room_id]['card_all'].remove(card)
                    # Пополняем список карточек пользователей на руках
                    rooms[room_id]['card_users'].append(card)
                    # Добавляем карточку в список карточек игрока
                    rooms[room_id]['players'][player].append(card)
                    bot.send_message(player, 'Новый раунд! Вам отправлены 6 карточек (одна из них новая).')
                    # Отправляем игрокам 6 карточек с изображениями а также делаем кнопки
                    buttons = types.InlineKeyboardMarkup(row_width=3)
                    imgs = []
                    for card in rooms[room_id]['players'][player]:
                        # Отправляем изображение игроку
                        imgs.append(telebot.types.InputMediaPhoto(open(f'img/{card}.jpg', 'rb'), caption=f'{card}'))
                        # bot.send_photo(player, open(f'img/{card}.jpg', 'rb'), caption=f'{card}')
                        buttons.add(types.InlineKeyboardButton(f'{card}', callback_data=f'№ {card}'))
                    bot.send_media_group(player, imgs)
                    bot.send_message(player,
                                     text=f'Ведущий загадывает карточку и называет ассоциацию.\nКаждый игрок (в том числе и ведущий) должен выбрать № карточки в соответсвии с названной ассоциацией (№ карточки в описании каждого фото).',
                                     reply_markup=buttons)
            else:
                bot.send_message(message.from_user.id, text='Ещё не все игроки сделали свой выбор, подождите')
        else:
            # Отправляем сообщение об ошибке
            bot.send_message(message.chat.id, 'Комната не найдена!')


# Функция отправки сообщений после выбора карт
def round_card(message):
    if message.from_user.id not in players_in_games:
        bot.send_message(message.from_user.id, text='Вы ещё не присоединились ни к одной из игр /start')
    elif len(rooms[players_in_games[message.from_user.id]]['players'][message.from_user.id]) == 5:
        bot.send_message(message.from_user.id, text='Ранее Вы уже сделали свой выбор, ждите!')
    else:
        # Получаем код комнаты из сообщения
        room_id = players_in_games[message.from_user.id]
        # Получаем номер выбранной карточки игрока
        card_choice = int(message.data.split()[1])
        if card_choice not in rooms[room_id]['players'][message.from_user.id]:
            bot.send_message(message.from_user.id, text='Вы пытаетесь выбрать карточку которой у вас нет!\nВаш выбор отменен!\nСделайте выбор из карточек последнего "выбора карточек"!')
        else:
            # Добавляем карту в список карт раунда
            rooms[room_id]['card_round'].append(card_choice)
            # Удаляем эту карту из списка карт всех игроков, а также у игрока
            rooms[room_id]['card_users'].remove(card_choice)
            rooms[room_id]['players'][message.from_user.id].remove(card_choice)
            # Получаем список игроков
            players = rooms[room_id]['players']
            if len(rooms[room_id]['card_round']) == len(players):
                # Отправляем игрокам по 1 карточке с изображениями, которые выбирали игроки
                for player in players:
                    # Генерируем случайное изображение из списка карточек раунда
                    card = random.choice(rooms[room_id]['card_round'])
                    # Удаляем выбранное изображение из списка карточек раунда
                    rooms[room_id]['card_round'].remove(card)
                    # Пополняем основной список карт освободившейся карточкой
                    rooms[room_id]['card_all'].append(card)
                    # Отправляем случайное изображение каждому игроку
                    bot.send_media_group(player, [telebot.types.InputMediaPhoto(open(f'img/stop.jpg', 'rb'), caption=f'Стоп карточка'),
                                                           telebot.types.InputMediaPhoto(open(f'img/{card}.jpg', 'rb'), caption=f'{card}')])
                    # bot.send_photo(player, open(f'img/{card}.jpg', 'rb'), caption=f'№ {card}')
                    bot.send_message(player, f'Все игроки выбрали по карточке!\nВам отправлена два фото: первое - это "Стоп карточка" для защиты от случайных прикосновений во время голосования, второе - это одна рандомная карточка из выбранных игроками с её номером.\nНужно открыть !второе фото! и выложить телефоны на стол и голосуем!\nПосле голосования обновляем карточки командой "Старт игры"')


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
Ведущий игрок раунда придумывает ассоциацию к одной из 6ти имеющихся у него карточек, говорит игрокам ассоциацию вслух, выбирает в меню бота номер выбранной карты.
Игроки выбирают свои карточки в соответствии с ассоциацией ведущего и делают выбор номера своей карточки в боте.
Когда все игроки сделали свой выбор - бот автоматически присылает каждому игроку одну из выбранных всеми игроками карт (карты присылаются рандомно, это может быть как ваша карта, так и чужая).
Игроки выкладывают телефоны с присланной карточкой на стол.
Происходит голосование, подсчет очков, ходы по полю.
Командой "Старт игры" объявляется новый раунд, бот заменяет использованные карточки и присылает новый набор из 6ти карточек каждому игроку.

Для перехода к главному меню всегда используйте команду /start'''
    bot.send_message(message.chat.id, text)


# Запускаем бота
if __name__ == '__main__':
    bot.polling(none_stop=True)









