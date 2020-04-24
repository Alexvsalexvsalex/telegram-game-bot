from telegram.ext import Updater, CommandHandler

users = []


def start(update, context):
    update.message.reply_text('Я ни че не умею, отстань')


def register(update, context):
    users.append(update.message.from_user.username)


def remove(update, context):
    users.remove(update.message.from_user.username)


def status(update, context):
    update.message.reply_text(users)


import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

if __name__ == "__main__":
    updater = Updater('1268400370:AAHHFMgsiN5n3PqUwjUbBRVtC4kNfl5MSTk', use_context=True)
    dp = updater.dispatcher

    # public handlers
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('register', register))
    dp.add_handler(CommandHandler('remove', remove))
    dp.add_handler(CommandHandler('status', status))

    updater.start_polling()
    updater.idle()
