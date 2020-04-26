from telegram.ext import Updater, CommandHandler
from logic import Match, Tournament

currentTournament = Tournament()
currentMatch = None


def reset(bot, update):
    global currentMatch
    global currentTournament
    currentTournament = Tournament()
    currentMatch = None
    update.message.reply_text('Турнир сброшен')


def test(bot, update):
    global currentMatch
    global currentTournamen
    update.message.reply_text('Проверка связи')


def startTournament(bot, update):
    global currentMatch
    global currentTournament
    if currentTournament.isStarted():
        update.message.reply_text('Турнир идёт')
    elif currentTournament.canBeStarted():
        currentTournament.start()
        update.message.reply_text('Турнир начался')
    else:
        update.message.reply_text('Турнир не может быть начат, минимум 2 участника')


def register(bot, update):
    global currentMatch
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


def nextMatch(bot, update):
    global currentMatch
    global currentTournament
    if currentTournament.isStarted():
        if currentMatch is not None:
            update.message.reply_text('Есть активный матч')
        else:
            currentMatch = currentTournament.getCurrentMatch()
            update.message.reply_text('Матч между @' + currentMatch.getFirstPlayer() + ' и @' + currentMatch.getSecondPlayer())
    else:
        update.message.reply_text('В данное время турнир не проводится')


def sendWinner(bot, update, args):
    global currentMatch
    global currentTournament
    if not currentTournament.isStarted():
        update.message.reply_text('В данное время турнир не проводится')
    else:
        if len(args) != 1:
            update.message.reply_text('Нужен только username победителя')
        else:
            if currentMatch is None:
                update.message.reply_text('Матч не начат')
            else:
                if currentMatch is None or (
                        args[0] != currentMatch.getFirstPlayer() and args[0] != currentMatch.getSecondPlayer()):
                    update.message.reply_text('Не знаем такого')
                else:
                    currentMatch.setWinner(args[0])
                    currentTournament.receiveMatchWinner(currentMatch)
                    currentMatch = None
                    checkTournamentEnd(update)


def iAmTheWinner(bot, update):
    global currentMatch
    global currentTournament
    if not currentTournament.isStarted():
        update.message.reply_text('В данное время турнир не проводится')
    else:
            if currentMatch is None:
                update.message.reply_text('Матч не начат')
            else:
                if currentMatch is None or (
                        update.message.from_user.username != currentMatch.getFirstPlayer() and
                        update.message.from_user.username != currentMatch.getSecondPlayer()):
                    update.message.reply_text('Не знаем такого')
                else:
                    currentMatch.setWinner(update.message.from_user.username)
                    currentTournament.receiveMatchWinner(currentMatch)
                    currentMatch = None
                    checkTournamentEnd(update)


def checkTournamentEnd(update):
    global currentMatch
    global currentTournament
    if currentTournament.isFinished():
        update.message.reply_text('Победитель турнира: @' + currentTournament.getWinner())
        currentTournament = Tournament()
        currentMatch = None
    else:
        update.message.reply_text('Продолжаем турнир')


def myHelp(bot, update):
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
    dp.add_handler(CommandHandler('start_tournament', startTournament))
    dp.add_handler(CommandHandler('register', register))
    dp.add_handler(CommandHandler('participants', participants))
    dp.add_handler(CommandHandler('reset', reset))
    dp.add_handler(CommandHandler('next_match', nextMatch))
    dp.add_handler(CommandHandler('i_am_the_winner', iAmTheWinner))
    dp.add_handler(CommandHandler('send_winner', sendWinner, pass_args=True))
    dp.add_handler(CommandHandler('help', myHelp))

    updater.start_polling()
    updater.idle()
