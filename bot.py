from telegram.ext import Updater, CommandHandler
from logic import Match, Tournament
import time


currentTournament = Tournament()


def reset(bot, update):
    global currentTournament
    currentTournament = Tournament()
    update.message.reply_text('Турнир завершен, открывается регистрация на новый')


def test(bot, update):
    update.message.reply_text('Проверка связи')


def start_tournament(bot, update):
    global currentTournament
    if currentTournament.isStarted():
        update.message.reply_text('Турнир идёт')
    elif currentTournament.canBeStarted():
        currentTournament.start()
        update.message.reply_text('Турнир начался')
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
    partLst = currentTournament.getParticipants()
    if len(partLst) == 0:
        update.message.reply_text("Нет зарегистрировашихся")
    else:
        message = "Список зарегистрировашихся: "
        for u in partLst:
            message += u + ' '
        update.message.reply_text(message)


def dice(bot, update):
    global currentTournament
    user = update.message.from_user.username
    chat_id = update.message.chat.id
    if currentTournament.getCurrentMatch().canBeChanged(user):
        number_on_dice = update.message.reply_dice().dice.value
        result = currentTournament.getCurrentMatch().setResult(user, number_on_dice)
        if result is not None:
            time.sleep(3)
            if result == "!":
                bot.sendMessage(chat_id, "Ого, похоже на ничью, переигровка!")
            else:
                bot.sendMessage(chat_id, "Побеждает @" + result)
            next_match(bot, chat_id)
    else:
        update.message.reply_text("Эм, но вы не участвуете в текущем матче, либо уже бросили кубик")


def next_match(bot, chat_id):
    global currentTournament
    if not check_tournament_end(bot, chat_id):
        players = currentTournament.getCurrentMatch().getPlayers()
        bot.sendMessage(chat_id, 'Матч между @' + players[0] + ' и @' + players[1])


def check_tournament_end(bot, chat_id):
    global currentTournament
    if currentTournament.isFinished():
        bot.sendMessage(chat_id, 'Победитель турнира: @' + currentTournament.getWinner())
        reset(bot, chat_id)
    else:
        bot.sendMessage(chat_id, 'Продолжаем турнир')


def my_help(bot, update):
    update.message.reply_text('Инструкция:\n'
                              '1) Для участия в турнире необходимо зарегистрироваться. Для этого воспользуйтесь командой /register\n'
                              '2) Турнир начинается командой /start_tournament . Регистрация после этого закрывается.\n'
                              '3) Чтобы провести матч необходимо выполнить команду /next_match. Будут определены участники матча\n'
                              '4) После проведения матча нужно сообщить победителя командой /send_winner с тэгом победителя. Сообщает сам победитель.\n'
                              '5) В форс-мажорных ситуациях можно сбросить текущий туринир командой /reset.\n'
                              '6) Также можно проверить работоспособность бота командой /test\n')


import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

if __name__ == "__main__":
    updater = Updater('1268400370:AAHHFMgsiN5n3PqUwjUbBRVtC4kNfl5MSTk')
    dp = updater.dispatcher

    # public handlers
    dp.add_handler(CommandHandler('test', test))
    dp.add_handler(CommandHandler('start_tournament', start_tournament))
    dp.add_handler(CommandHandler('register', register))
    dp.add_handler(CommandHandler('participants', participants))
    dp.add_handler(CommandHandler('reset', reset))
    dp.add_handler(CommandHandler('dice', dice))
    dp.add_handler(CommandHandler('help', my_help))

    updater.start_polling()
    updater.idle()
