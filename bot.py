from telegram.ext import Updater, CommandHandler
from logic import Match, Tournament
import time
import shelve
import random


currentTournament = Tournament()
current_emoji = ":dice"

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


def hard_reset(bot, chat_id):
    global currentTournament
    currentTournament = Tournament()
    bot.sendMessage(chat_id, random.choice(begin_registration_messages))


def reset(bot, update):
    hard_reset(bot, update.message.chat.id)


def test(bot, update):
    update.message.reply_text(random.choice(test_messages))


def start_tournament(bot, update, args):
    global currentTournament
    global current_emoji
    if currentTournament.isStarted():
        update.message.reply_text(random.choice(tournament_is_running_messages))
    elif currentTournament.canBeStarted():
        if len(args) == 1 and args[0] == "darts":
            current_emoji = ":dart:"  # Here dart emoji
        else:
            current_emoji = ":dice:"  # Here dice emoji
        currentTournament.start()
        chat_id = update.message.chat.id
        bot.sendMessage(chat_id, random.choice(success_start_tournament_messages))
        next_match(bot, chat_id)
    else:
        update.message.reply_text(random.choice(few_participants_messages))


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
    with shelve.open('winners') as winners_map:
        for p in winners_map:
            answer.append(p + ': ' + str(winners_map[p]))
    bot.sendMessage(update.message.chat.id, random.choice(statistics_messages) + '\n' + '\n'.join(answer))


def throw(bot, update):
    global currentTournament
    global current_emoji
    if currentTournament.isStarted():
        user = update.message.from_user.username
        chat_id = update.message.chat.id
        if currentTournament.getCurrentMatch().canBeChanged(user):
            number_on_dice = update.message.reply_dice(emoji = current_emoji).dice.value
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
        with shelve.open('winners') as winners_map:
            winners_map[winner] = winners_map.get(winner, 0) + 1
        hard_reset(bot, chat_id)


def my_help(bot, update):
    update.message.reply_text(
        '1) Для участия в турнире необходимо зарегистрироваться. Для этого воспользуйтесь командой /register. \n'
        '2) Можно узнать список участников, вызвав команду /participants. \n'
        '3) Турнир начинается командой /start_tournament. Регистрация после этого закрывается.\n'
        '4) Можно указать вид состязания, указав соответствующий эмоджи в команде /start_tournament. По умолчанию это кости. (В разработке) \n'
        '5) В начале матча будут объявлены игроки. Чтобы сделать ход воспользуйтесь командой /throw. \n'
        '6) В форс-мажорных ситуациях можно сбросить текущий туринир командой /reset.\n'
        '7) Также можно проверить работоспособность бота командой /test. \n')


import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

if __name__ == "__main__":
    updater = Updater('1268400370:AAHHFMgsiN5n3PqUwjUbBRVtC4kNfl5MSTk')
    dp = updater.dispatcher

    # public handlers
    dp.add_handler(CommandHandler('test', test))
    dp.add_handler(CommandHandler('start_tournament', start_tournament, pass_args=True))
    dp.add_handler(CommandHandler('register', register))
    dp.add_handler(CommandHandler('participants', participants))
    dp.add_handler(CommandHandler('reset', reset))
    dp.add_handler(CommandHandler('stats', stats))
    dp.add_handler(CommandHandler('throw', throw))
    dp.add_handler(CommandHandler('help', my_help))

    updater.start_polling()
    updater.idle()
