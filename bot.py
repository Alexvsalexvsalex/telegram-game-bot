from telegram.ext import Updater, CommandHandler
from logic import Match, Tournament
import time
import shelve


currentTournament = Tournament()
current_emoji = ":dice"


def hard_reset(bot, chat_id):
    global currentTournament
    currentTournament = Tournament()
    bot.sendMessage(chat_id, 'Турнир завершен, открывается регистрация на новый')


def reset(bot, update):
    hard_reset(bot, update.message.chat.id)


def test(bot, update):
    update.message.reply_text('Проверка связи')


def start_tournament(bot, update, args):
    global currentTournament
    global current_emoji
    if currentTournament.isStarted():
        update.message.reply_text('Турнир идёт')
    elif currentTournament.canBeStarted():
        if len(args) == 1 and args[0] == "darts":
            current_emoji = ":dart:"  # Here dart emoji
        else:
            current_emoji = ":dice:"  # Here dice emoji
        currentTournament.start()
        chat_id = update.message.chat.id
        bot.sendMessage(chat_id, 'Турнир начался')
        next_match(bot, chat_id)
    else:
        update.message.reply_text('Турнир не может быть начат, минимум 2 участника')


def register(bot, update):
    global currentTournament
    if not currentTournament.isStarted():
        currentTournament.register(update.message.from_user.username)
        update.message.reply_text('Успешная регистрация на этот замечательный турнир')
    else:
        update.message.reply_text('Турнир идёт')


def participants(bot, update):
    global currentTournament
    part_list = currentTournament.getParticipants()
    if len(part_list) == 0:
        update.message.reply_text("Нет зарегистрировавшихся")
    else:
        message = "Список зарегистрировавшихся: "
        for u in part_list:
            message += u + ' '
        update.message.reply_text(message)


def stats(bot, update):
    answer = []
    with shelve.open('winners') as winners_map:
        for p in winners_map:
            answer.append(p + ': ' + str(winners_map[p]))
    bot.sendMessage(update.message.chat.id, 'Статистика:\n' + '\n'.join(answer))


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
                time.sleep(4)
                if result == "!":
                    bot.sendMessage(chat_id, "Ого, похоже на ничью, переигровка!")
                else:
                    bot.sendMessage(chat_id, "Побеждает @" + result)
                    next_match(bot, chat_id)
        else:
            update.message.reply_text("Эм, но вы не участвуете в текущем матче, либо уже сделали ход")
    else:
        update.message.reply_text("Турнир еще не начался")


def next_match(bot, chat_id):
    global currentTournament
    if not currentTournament.isFinished():
        players = currentTournament.getCurrentMatch().getPlayers()
        bot.sendMessage(chat_id, 'Матч между @' + players[0] + ' и @' + players[1])
    else:
        winner = currentTournament.getWinner()
        bot.sendMessage(chat_id, 'Победитель турнира: @' + winner)
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
