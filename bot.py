from telegram.ext import Updater, CommandHandler
from logic import Match, Tournament
import time
import shelve
import random
import os
import logging
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']
currentTournament = Tournament()
current_emoji = "🎲"

test_messages = ['Проверка связи', 'Ало, ало, как слышно']
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


def hard_reset(bot, chat_id):
    global currentTournament
    currentTournament = Tournament()
    bot.sendMessage(chat_id, random.choice(begin_registration_messages))


def reset(bot, update):
    hard_reset(bot, update.message.chat.id)


def test(bot, update):
    update.message.reply_text(random.choice(test_messages))


def start_tournament(bot, update):
    global currentTournament
    global current_emoji
    if currentTournament.isStarted():
        update.message.reply_text(random.choice(tournament_is_running_messages))
    elif currentTournament.canBeStarted():
        currentTournament.start()
        chat_id = update.message.chat.id
        bot.sendMessage(chat_id, random.choice(success_start_tournament_messages))
        next_match(bot, chat_id)
    else:
        update.message.reply_text(random.choice(few_participants_messages))


def set_emoji(bot, update, args):
    global current_emoji
    if len(args) == 1:
        if args[0] == "dart":
            current_emoji = "🎯"  # Here dart emoji
            update.message.reply_text(random.choice(set_emoji_dart))
        elif args[0] == "dice":
            current_emoji = "🎲"  # Here dice emoji
            update.message.reply_text(random.choice(set_emoji_dice))
        elif args[0] == "basketball":
            current_emoji = "🏀"  # Here basketball emoji
            update.message.reply_text(random.choice(set_emoji_basketball))
        else:
            update.message.reply_text(random.choice(wrong_arguments))
    else:
        update.message.reply_text(random.choice(wrong_arguments))


def register(bot, update):
    global currentTournament
    if not currentTournament.isStarted():
        currentTournament.register(update.message.from_user.username)
        update.message.reply_text(random.choice(success_registration_messages))
    else:
        update.message.reply_text(random.choice(tournament_is_running_messages))


def participants(bot, update):
    global currentTournament
    part_list = currentTournament.getParticipants()
    if len(part_list) == 0:
        update.message.reply_text(random.choice(no_registrations_messages))
    else:
        message = random.choice(list_registrations_messages)
        for u in part_list:
            message += u + ' '
        update.message.reply_text(message)


def stats(bot, update):
    answer = []
    with psycopg2.connect(DATABASE_URL, sslmode='require') as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM winners')
            for p in cur:
                answer.append(p[0] + ' --- ' + str(p[1]))
    bot.sendMessage(update.message.chat.id, random.choice(statistics_messages) + '\n' + '\n'.join(answer))


def throw(bot, update):
    global currentTournament
    global current_emoji
    if currentTournament.isStarted():
        user = update.message.from_user.username
        chat_id = update.message.chat.id
        if currentTournament.getCurrentMatch().canBeChanged(user):
            number_on_dice = update.message.reply_dice(emoji=current_emoji).dice.value
            result = currentTournament.getCurrentMatch().setResult(user, number_on_dice)
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
    if not currentTournament.isFinished():
        players = currentTournament.getCurrentMatch().getPlayers()
        bot.sendMessage(chat_id, random.choice(match_notify_messages) + ' @' + players[0] + ' и @' + players[1])
    else:
        winner = currentTournament.getWinner()
        bot.sendMessage(chat_id, random.choice(tournament_winner_messages) + ' @' + winner)
        with psycopg2.connect(DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count FROM winners WHERE username = %s", (winner, ))
                rows = cur.fetchall()
                if len(rows) > 0:
                    cur.execute("UPDATE winners SET count = count + 1 WHERE username = %s", (winner, ))
                else:
                    cur.execute("INSERT INTO winners (username, count) VALUES (%s, %s)", (winner, 1, ))
        hard_reset(bot, chat_id)


def my_help(bot, update):
    update.message.reply_text(
        '1) Для участия в турнире необходимо зарегистрироваться. Для этого воспользуйтесь командой /register. \n'
        '2) Можно узнать список участников, вызвав команду /participants. \n'
        '3) Турнир начинается командой /start_tournament. Регистрация после этого закрывается.\n'
        '4) Можно указать вид состязания, указав соответствующий эмоджи в команде /set_emoji. По умолчанию это кости. \n'
        '5) В начале матча будут объявлены игроки. Чтобы сделать ход воспользуйтесь командой /throw. \n'
        '6) В форс-мажорных ситуациях можно сбросить текущий туринир командой /reset.\n'
        '7) Также можно проверить работоспособность бота командой /test. \n')


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

if __name__ == "__main__":
    updater = Updater(os.environ["TOURNAMENT_BOT_TOKEN"])
    dp = updater.dispatcher

    # public handlers
    dp.add_handler(CommandHandler('test', test))
    dp.add_handler(CommandHandler('start_tournament', start_tournament))
    dp.add_handler(CommandHandler('register', register))
    dp.add_handler(CommandHandler('participants', participants))
    dp.add_handler(CommandHandler('reset', reset))
    dp.add_handler(CommandHandler('stats', stats))
    dp.add_handler(CommandHandler('throw', throw))
    dp.add_handler(CommandHandler('set_emoji', set_emoji, pass_args=True))
    dp.add_handler(CommandHandler('help', my_help))

    updater.start_polling()
    updater.idle()
