from telegram.ext import Updater, CommandHandler
from logic import Match, Tournament

currentTournament = Tournament()
currentMatch = None


def reset(bot, update):
    global currentMatch
    global currentTournament
    currentTournament = Tournament()
    currentMatch = None


def test(bot, update):
    global currentMatch
    global currentTournament
    update.message.reply_text('Проверка связи')


def start(bot, update):
    global currentMatch
    global currentTournament
    currentTournament.start()


def register(bot, update):
    global currentMatch
    global currentTournament
    currentTournament.register(update.message.from_user.username)


def nextMatch(bot, update):
    global currentMatch
    global currentTournament
    if currentMatch is not None:
        update.message.reply_text('Есть активный матч')
    else:
        currentMatch = currentTournament.getCurrentMatch()
        update.message.reply_text('Матч между ' + currentMatch.getFirstPlayer() + ' ' + currentMatch.getSecondPlayer())


def sendWinner(bot, update, args):
    global currentMatch
    global currentTournament
    if args.length != 1:
        update.message.reply_text('Нужен только username победителя')
    else:
        if currentMatch is None:
            update.message.reply_text('Матч не начат')
        else:
            if currentMatch is None or args[0] != currentMatch.getFirstPlayer() or args[0] != currentMatch.getSecondPlayer():
                update.message.reply_text('Не знаем такого')
            else:
                currentMatch.setWinner(args[0])
                currentTournament.receiveMatchWinner(currentMatch)
                currentMatch = None
                checkTournamentEnd(update)


def checkTournamentEnd(update):
    global currentMatch
    global currentTournament
    if currentTournament.isFinished():
        update.message.reply_text('Иии... Победитель: ' + currentTournament.getWinner())
    else:
        update.message.reply_text('Продолжаем турнир')


import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

if __name__ == "__main__":
    updater = Updater('1268400370:AAHHFMgsiN5n3PqUwjUbBRVtC4kNfl5MSTk')
    dp = updater.dispatcher

    # public handlers
    dp.add_handler(CommandHandler('test', test))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('register', register))
    dp.add_handler(CommandHandler('reset', reset))
    dp.add_handler(CommandHandler('nextMatch', nextMatch))
    dp.add_handler(CommandHandler('sendWinner', sendWinner, pass_args=True))

    updater.start_polling()
    updater.idle()
