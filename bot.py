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
match_deadline = 0

hello_messages = ["Hello, %s", "%s ආයුබෝවන්", "Բարեւ, %s", "مرحبا %s", "Салом %s", "Здраво %s", "Здравейте %s",
                  "Прывітанне %s", "Привіт %s", "Привет, %s", "Поздрав %s", "سلام به %s", "שלום %s", "Γεια σας %s",
                  "העלא %s", "ہیل%s٪ ے", "Bonjour %s", "Bună ziua %s", "Ciao %s", "Dia duit %s",
                  "Dobrý deň %s", "Habari %s", "Halló %s", "Halo %s", "Hei %s", "Hej %s",
                  "Helo %s", "Hola %s", "Kaixo %s", "Kamusta %s", "Merhaba %s",
                  "Olá %s", "Përshëndetje %s", "Pozdrav %s", "Pozdravljeni %s", "Sawubona %s",
                  "Sveiki %s", "Tere %s", "Witaj %s", "Xin chào %s", "ສະບາຍດີ %s", "สวัสดี %s", "ഹലോ %s", "ಹಲೋ %s",
                  "హలో %s", "हॅलो %s", "नमस्कार%sको", "হ্যালো %s", "ਹੈਲੋ %s", "હેલો %s", "வணக்கம் %s"]
success_start_tournament_messages = ['Турнир начался', 'Давайте-ка начнем играть']
tournament_is_running_messages = ['Турнир идёт', 'Существует активный турнир', 'Турнир уже начался']
begin_registration_messages = ['Турнир завершен, открывается регистрация на новый', 'Ожидаем желающих посоревноваться']
success_registration_messages = ['Успешная регистрация на турнир', 'Проходите, присаживайтесь']
already_registered_messages = ['Вы уже в турнире, зачем обманывать?', 'Не нужно регистрироваться несколько раз']
few_participants_messages = ['Турнир не может быть начат, минимум 2 участника', 'Мало игроков, ждём-с']
no_registrations_messages = ['Нет зарегистрировавшихся', 'Никто не хочет играть(']
list_registrations_messages = ['Список зарегистрировавшихся: %s']
statistics_messages = ['Статистика:', 'Взглянем на ваши успехи']
draw_messages = ['Ого, похоже на ничью. %s и %s, переигровка!', 'Опять админ подкручивает, %s и %s, давайте заново']
match_winner_messages = ['%s побеждает', 'Победитель матча: %s']
early_messages = ['Давайте ещё немного подождём участников матча', '1 минута не прошла...']
not_your_turn_messages = ['Эм, но вы не участвуете в текущем матче, либо уже сделали ход',
                          'Извините, сейчас не ваш ход', 'NotYourTurnException']
not_started_tournament_messages = ['Турнир еще не начался', 'Рано, нет действующих турниров']
match_notify_messages = ['Матч между %s и %s', '%s vs %s, это будет интересно']
tournament_winner_messages = ['Победитель турнира: %s', 'Поздравляем, %s']
set_emoji_dart = ['Давайте покидаем дротики', 'Теперь играем в дартс']
set_emoji_dice = ['С этого момента кидаем кости', 'Готовьте ваши кубики']
set_emoji_basketball = ['Тренер, где кольцо?', 'Я Куроко Тецуя, и это мой басктебол!']
wrong_arguments = ['Неверные аргументы']

time_for_turn_seconds = 60

dice_names = ['кости', 'кубики', 'кубик', 'dice', 'dices']
dart_names = ['дартс', 'dart', 'darts']
basketball_names = ['баскетбол', 'basketball', 'basket', 'ball']


def hard_reset(bot, chat_id):
    global currentTournament
    currentTournament = Tournament()
    bot.sendMessage(chat_id, random.choice(begin_registration_messages))


def reset(bot, update):
    global match_deadline
    if match_deadline < time.time():
        hard_reset(bot, update.message.chat.id)
    else:
        update.message.reply_text(random.choice(early_messages))


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
    if len(args) == 0:
        set_emoji(bot, update, random.choice(random.choice([dice_names, dart_names, basketball_names])))
    elif len(args) == 1:
        arg = args[0].lower()
        if arg in dart_names:
            current_emoji = "🎯"  # Here dart emoji
            update.message.reply_text(random.choice(set_emoji_dart))
        elif arg in dice_names:
            current_emoji = "🎲"  # Here dice emoji
            update.message.reply_text(random.choice(set_emoji_dice))
        elif arg in basketball_names:
            current_emoji = "🏀"  # Here basketball emoji
            update.message.reply_text(random.choice(set_emoji_basketball))
        else:
            update.message.reply_text(random.choice(wrong_arguments))
    else:
        update.message.reply_text(random.choice(wrong_arguments))


def register(bot, update):
    global currentTournament
    if not currentTournament.is_started():
        player = update.message.from_user.username
        if not currentTournament.is_registered(player):
            currentTournament.register(player)
            update.message.reply_text(random.choice(success_registration_messages))
        else:
            update.message.reply_text(random.choice(already_registered_messages))
    else:
        update.message.reply_text(random.choice(tournament_is_running_messages))


def participants(bot, update):
    global currentTournament
    part_list = currentTournament.get_participants()
    if len(part_list) == 0:
        update.message.reply_text(random.choice(no_registrations_messages))
    else:
        message = random.choice(list_registrations_messages)
        update.message.reply_text(message % (', '.join(part_list)))


def get_text_stats(stats):
    # (username, tournament_points, tournament_wins, number_matches, number_wins, sum_value, number_tournaments)
    prepared_stat1 = []
    prepared_stat2 = []
    for p in stats:
        if p[3] != 0:
            prepared_stat1.append([p[0], p[3], str(p[4] * 100 // p[3]) + '%', p[5] * 10 // p[3] / 10, p[4]])
        if p[6] != 0:
            prepared_stat2.append([p[0], p[6], str(p[2] * 100 // p[6]) + '%', p[1]])
    prepared_stat1.sort(key=lambda x: -x[4])
    prepared_stat2.sort(key=lambda x: -x[3])
    for i in range(len(prepared_stat1)):
        prepared_stat1[i].pop()
    prepared_stat1.insert(0, ['NAME', 'NM', 'MWR', 'AVG'])
    prepared_stat2.insert(0, ['NAME', 'NT', 'TWR', 'TP'])
    return '<pre>' + \
           tabulate(prepared_stat1, tablefmt="simple", numalign="left", colalign="left", floatfmt=".1f") + '\n' + \
           tabulate(prepared_stat2, tablefmt="simple", numalign="left", colalign="left", floatfmt=".1f") + '</pre>'


def stats(bot, update):
    with psycopg2.connect(DATABASE_URL, sslmode='require') as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT * FROM winners')
            bot.sendMessage(update.message.chat.id, random.choice(statistics_messages) + '\n' + get_text_stats(cur),
                            parse_mode=telegram.ParseMode.HTML)


def throw(bot, update):
    global currentTournament
    global current_emoji
    if currentTournament.is_started():
        user = update.message.from_user.username
        chat_id = update.message.chat.id
        if currentTournament.get_current_match().can_be_changed(user):
            number_on_dice = update.message.reply_dice(emoji=current_emoji).dice.value
            if number_on_dice >= 4:
                number_on_dice = 6
            else:
                number_on_dice = 1
            result = currentTournament.get_current_match().set_result(user, number_on_dice)
            if result is not None:
                time.sleep(5)
                if result == "!":
                    refresh_match_deadline()
                    bot.sendMessage(chat_id, random.choice(draw_messages) % (
                        currentTournament.get_current_match().get_players()))
                else:
                    bot.sendMessage(chat_id, random.choice(match_winner_messages) % (result))
                    next_match(bot, chat_id)
        else:
            update.message.reply_text(random.choice(not_your_turn_messages))
    else:
        update.message.reply_text(random.choice(not_started_tournament_messages))


def refresh_match_deadline():
    global match_deadline
    match_deadline = time.time() + time_for_turn_seconds


def next_match(bot, chat_id):
    global currentTournament
    global match_deadline
    if not currentTournament.is_finished():
        players = currentTournament.get_current_match().get_players()
        refresh_match_deadline()
        bot.sendMessage(chat_id, random.choice(match_notify_messages) % ('@' + players[0], '@' + players[1]))
    else:
        winner = currentTournament.get_winner()
        stats = currentTournament.get_stats()
        bot.sendMessage(chat_id, random.choice(tournament_winner_messages) + ' @' + winner)
        with psycopg2.connect(DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                for username in stats:
                    cur.execute(
                        "INSERT INTO winners (username, tournament_points, tournament_wins, number_tournaments, number_matches, number_wins, sum_value) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING", (username, 0, 0, 0, 0, 0, 0))
                    user_stats = stats[username]
                    cur.execute("UPDATE winners "
                                "SET (tournament_points, tournament_wins, number_tournaments, number_matches, number_wins, sum_value) ="
                                " (tournament_points + %s, tournament_wins + %s, number_tournaments + %s, number_matches + %s, number_wins + %s, sum_value + %s)"
                                " WHERE username = %s",
                                (user_stats['tournament_points'], user_stats['tournament_wins'],
                                 user_stats['number_tournaments'],
                                 user_stats['number_matches'], user_stats['number_wins'], user_stats['sum_value'],
                                 username))
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
        'NT = Number of Tournaments\n'
        'TWR = Tournament Win Rate\n'
        'TP = Tournament Points\n'
        'NM = Number of Matches\n'
        'MWR = Match Win Rate\n'
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
