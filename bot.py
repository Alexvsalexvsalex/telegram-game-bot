import telegram
from telegram.ext import Updater, CommandHandler
from logic import Match, Tournament
import time
from tabulate import tabulate
import random
import os
import logging
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']
currentTournament = Tournament()
current_emoji = "🎲"

hello_messages = ["Hello, %s", "%s ආයුබෝවන්", "Բարեւ, %s", "مرحبا %s", "Салом %s", "Здраво %s", "Здравейте %s",
                 "Прывітанне %s", "Привіт %s", "Привет, %s", "Поздрав %s", "سلام به %s", "שלום %s", "Γεια σας %s",
                 "העלא %s", "ہیل%s٪ ے", "Bonjou %s", "Bonjour %s", "Bună ziua %s", "Ciao %s", "Dia duit %s",
                 "Dobrý deň %s", "Dobrý den, %s", "Habari %s", "Halló %s", "Hallo %s", "Halo %s", "Hei %s", "Hej %s",
                 "Helo %s", "Hola %s", "Kaixo %s", "Kamusta %s", "Merhaba %s",
                 "Olá %s", "Ola %s", "Përshëndetje %s", "Pozdrav %s", "Pozdravljeni %s", "Salom %s", "Sawubona %s",
                 "Sveiki %s", "Tere %s", "Witaj %s", "Xin chào %s", "ສະບາຍດີ %s", "สวัสดี %s", "ഹലോ %s", "ಹಲೋ %s",
                 "హలో %s", "हॅलो %s", "नमस्कार%sको", "হ্যালো %s", "ਹੈਲੋ %s", "હેલો %s", "வணக்கம் %s",
                 "ကို %s မင်္ဂလာပါ", "გამარჯობა %s", "ជំរាបសួរ %s បាន", "こんにちは%s", "你好%s", "안녕하세요  %s"]
success_start_tournament_messages = ['Турнир начался', 'Давайте-ка начнем играть']
tournament_is_running_messages = ['Турнир идёт', 'Существует активный турнир']
begin_registration_messages = ['Турнир завершен, открывается регистрация на новый', 'Ожидаем желающих посоревноваться']
success_registration_messages = ['Успешная регистрация на этот замечательный турнир', 'Проходите, присаживайтесь']
few_participants_messages = ['Турнир не может быть начат, минимум 2 участника', 'Мало игроков, ждём-с']
no_registrations_messages = ['Нет зарегистрировавшихся', 'Никто не хочет играть(']
list_registrations_messages = ['Список зарегистрировавшихся: ']
statistics_messages = ['Статистика:']
draw_messages = ['Ого, похоже на ничью, переигровка!', 'Опять админ подкручивает, давайте заново']
match_winner_messages = ['И побеждает', 'Победитель матча']
not_your_turn_messages = ['Эм, но вы не участвуете в текущем матче, либо уже сделали ход', 'Извините, сейчас не ваш ход']
not_started_tournament_messages = ['Турнир еще не начался', 'Рано, нет действующих турниров']
match_notify_messages = ['Матч между', 'Объявляется противостояние ']
tournament_winner_messages = ['Победитель турнира:', 'Поздравляем, ']
set_emoji_dart = ['Давайте покидаем дротики', 'Теперь играем в дартс']
set_emoji_dice = ['С этого момента кидаем кости', 'Готовьте ваши кубики, будем играть']
set_emoji_basketball = ['Тренер, где кольцо?', 'Я Куроко Тецуя, и это мой басктебол!']
wrong_arguments = ['Неверные аргументы']

dice_names = ['кости', 'dice', 'dices']
dart_name = ['дартс', 'dart', 'darts']
basketball_name = ['баскетбол', 'basketball', 'basket', 'ball']


def hard_reset(bot, chat_id):
    global currentTournament
    currentTournament = Tournament()
    bot.sendMessage(chat_id, random.choice(begin_registration_messages))


def reset(bot, update):
    hard_reset(bot, update.message.chat.id)


def test(bot, update):
    update.message.reply_text(random.choice(hello_messages) % (update.message.from_user.first_name))


def start_tournament(bot, update):
    global currentTournament
    global current_emoji
    if currentTournament.is_started():
        update.message.reply_text(random.choice(tournament_is_running_messages))
    elif currentTournament.can_be_started():
        currentTournament.start()
        chat_id = update.message.chat.id
        bot.sendMessage(chat_id, random.choice(success_start_tournament_messages))
        next_match(bot, chat_id)
    else:
        update.message.reply_text(random.choice(few_participants_messages))


def set_emoji(bot, update, args):
    global current_emoji
    if len(args) == 1:
        if args[0].lower() in dart_name:
            current_emoji = "🎯"  # Here dart emoji
            update.message.reply_text(random.choice(set_emoji_dart))
        elif args[0].lower() in dice_names:
            current_emoji = "🎲"  # Here dice emoji
            update.message.reply_text(random.choice(set_emoji_dice))
        elif args[0].lower() in basketball_name:
            current_emoji = "🏀"  # Here basketball emoji
            update.message.reply_text(random.choice(set_emoji_basketball))
        else:
            update.message.reply_text(random.choice(wrong_arguments))
    else:
        update.message.reply_text(random.choice(wrong_arguments))


def register(bot, update):
    global currentTournament
    if not currentTournament.is_started():
        currentTournament.register(update.message.from_user.username)
        update.message.reply_text(random.choice(success_registration_messages))
    else:
        update.message.reply_text(random.choice(tournament_is_running_messages))


def participants(bot, update):
    global currentTournament
    part_list = currentTournament.get_participants()
    if len(part_list) == 0:
        update.message.reply_text(random.choice(no_registrations_messages))
    else:
        message = random.choice(list_registrations_messages)
        for u in part_list:
            message += u + ' '
        update.message.reply_text(message)


def get_text_stats(stats):
    prepared_stat = []
    for p in stats:
        if p[3] != 0:
            prepared_stat.append([p[0], p[1], p[2], p[3], str(p[4] * 100 / p[3]) + '%', p[5] / p[3]])
    return '<pre>' + tabulate(prepared_stat, headers=['NAME', 'T_P', 'T_W', 'N_M', 'W_R', 'AVG'], tablefmt="simple", numalign="right", colalign="right", floatfmt=".1f") + '</pre>'


def stats(bot, update):
    with psycopg2.connect(DATABASE_URL, sslmode='require') as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM winners')
            bot.sendMessage(update.message.chat.id, random.choice(statistics_messages) + '\n' + get_text_stats(cur), parse_mode=telegram.ParseMode.HTML)


def throw(bot, update):
    global currentTournament
    global current_emoji
    if currentTournament.is_started():
        user = update.message.from_user.username
        chat_id = update.message.chat.id
        if currentTournament.get_current_match().can_be_changed(user):
            number_on_dice = update.message.reply_dice(emoji=current_emoji).dice.value
            result = currentTournament.get_current_match().set_result(user, number_on_dice)
            if result is not None:
                time.sleep(5)
                if result == "!":
                    bot.sendMessage(chat_id, random.choice(draw_messages))
                else:
                    bot.sendMessage(chat_id, random.choice(match_winner_messages) + " @" + result)
                    next_match(bot, chat_id)
        else:
            update.message.reply_text(random.choice(not_your_turn_messages))
    else:
        update.message.reply_text(random.choice(not_started_tournament_messages))


def next_match(bot, chat_id):
    global currentTournament
    if not currentTournament.is_finished():
        players = currentTournament.get_current_match().get_players()
        bot.sendMessage(chat_id, random.choice(match_notify_messages) + ' @' + players[0] + ' и @' + players[1])
    else:
        winner = currentTournament.get_winner()
        stats = currentTournament.get_stats()
        bot.sendMessage(chat_id, random.choice(tournament_winner_messages) + ' @' + winner)
        with psycopg2.connect(DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                for username in stats:
                    cur.execute("INSERT INTO winners (username, tournament_points, tournament_wins, number_matches, number_wins, sum_value) "
                                "VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING", (username, 0, 0, 0, 0, 0))
                    user_stats = stats[username]
                    cur.execute("UPDATE winners "
                                "SET (tournament_points, tournament_wins, number_matches, number_wins, sum_value) ="
                                " (tournament_points + %s, tournament_wins + %s, number_matches + %s, number_wins + %s, sum_value + %s)"
                                " WHERE username = %s",
                                (user_stats['tournament_points'], user_stats['tournament_wins'], user_stats['number_matches'], user_stats['number_wins'], user_stats['sum_value'], username))
        hard_reset(bot, chat_id)


def my_help(bot, update):
    update.message.reply_text(
        '1) Для участия в турнире необходимо зарегистрироваться. Для этого воспользуйтесь командой /register. \n'
        '2) Можно узнать список участников, вызвав команду /participants. \n'
        '3) Турнир начинается командой /begin. Регистрация после этого закрывается.\n'
        '4) Можно указать вид состязания, командой с аргументом /emoji dice|dart|basketball. \n'
        '5) В начале матча будут объявлены игроки. Чтобы сделать ход воспользуйтесь командой /throw. \n'
        '6) В форс-мажорных ситуациях можно сбросить текущий туринир командой /drop.\n'
        '7) Ознакомьтесь со статистикой игроков командой /stat. \n'
        'TP = Tournament Points\n'
        'TW = Tournament Wins\n'
        'MW = Match Wins\n'
        'WR = Win Rate\n'
        'AVG = Average value\n'
        '8) Также можно поздороваться с ботом командой /greeting. Заодно узнаете не спит ли он. \n')


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

if __name__ == "__main__":
    updater = Updater(os.environ["TOURNAMENT_BOT_TOKEN"])
    dp = updater.dispatcher

    # public handlers
    dp.add_handler(CommandHandler('greeting', test))
    dp.add_handler(CommandHandler('begin', start_tournament))
    dp.add_handler(CommandHandler('register', register))
    dp.add_handler(CommandHandler('participants', participants))
    dp.add_handler(CommandHandler('drop', reset))
    dp.add_handler(CommandHandler('stat', stats))
    dp.add_handler(CommandHandler('throw', throw))
    dp.add_handler(CommandHandler('emoji', set_emoji, pass_args=True))
    dp.add_handler(CommandHandler('help', my_help))

    updater.start_polling()
    updater.idle()
