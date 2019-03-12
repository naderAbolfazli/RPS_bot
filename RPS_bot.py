#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import random

from telegram import (ReplyKeyboardMarkup, Bot, Update)
from telegram.ext import (Updater, CommandHandler, RegexHandler,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger()

ROUND_STATS, ROUND_NUMBER = range(2)


# waited_players = {}


def start(bot: Bot, update: Update, user_data):
    user_data['round'] = 0
    user_data['user_win'] = 0
    user_data['bot_win'] = 0
    update.message.reply_text("welcome to rps.\nwhat number of rounds do you want to play")
    # if waited_players.__len__():
    return ROUND_NUMBER
    # else:
    #     waited_players[update.message.chat_id] = (bot, update)


def round_number(bot, update, user_data):
    user_data['number_of_rounds'] = int(update.message.text)
    return start_round(bot, update, user_data)


def start_round(bot, update, user_data):
    user_data['round'] += 1
    reply_keyboard = [['Rock', 'Paper', 'Scissor']]
    logger.info("round started")
    update.message.reply_text("opponent ready, select one of the below for round *{}*".format(user_data['round']),
                              reply_markup=ReplyKeyboardMarkup(keyboard=reply_keyboard))
    return ROUND_STATS


def get_bot_random_choose():
    return ['Rock', 'Paper', 'Scissor'][random.randint(0, 2)]


def round_judgment(user_choice, bot_choice):
    return {
        ("Rock", "Rock"): 0,
        ("Rock", "Paper"): -1,
        ("Rock", "Scissor"): 1,
        ("Paper", "Paper"): 0,
        ("Paper", "Rock"): 1,
        ("Paper", "Scissor"): -1,
        ("Scissor", "Scissor"): 0,
        ("Scissor", "Rock"): -1,
        ("Scissor", "Paper"): 1,
    }[(user_choice, bot_choice)]


def get_win_or_lose(r_stat):
    return {
        1: "Win",
        -1: "Lose",
        0: "Tie"
    }[r_stat]


def r_stat_calculation(r_stat, user_data):
    if r_stat == 1:
        user_data['user_win'] += 1
    if r_stat == -1:
        user_data['bot_win'] += 1


def round_stats(bot, update, user_data):
    player_choice = update.message.text
    bot_choice = get_bot_random_choose()
    r_stat = round_judgment(player_choice, bot_choice)
    r_stat_calculation(r_stat, user_data)
    logger.info("waiting for next round")
    update.message.reply_text(
        'bot selected *{}*\n you *{}* round {}  '.format(bot_choice, get_win_or_lose(r_stat), user_data['round']))

    if user_data['round'] == user_data['number_of_rounds']:
        return game_stats(bot, update, user_data)
    else:
        start_round(bot, update, user_data)


def game_stats(bot, update, user_data):
    if user_data['user_win'] > user_data['bot_win']:
        result = "WIN"
    elif user_data['user_win'] < user_data['bot_win']:
        result = "LOSE"
    else:
        result = "Tie"

    update.message.reply_text('You *{}*'.format(result))
    return ConversationHandler.END


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.')

    return ConversationHandler.END


def error(bot, update):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, update.message)


def main():
    # Create the Updater and pass it your bot's token.
    bot = Bot(token="Token",
              base_url="https://tapi.bale.ai/",
              base_file_url="https://tapi.bale.ai/file/")
    updater = Updater(bot=bot)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_user_data=True)],

        states={
            ROUND_STATS: [RegexHandler(pattern='^(Rock|Paper|Scissor)$', callback=round_stats, pass_user_data=True)],
            ROUND_NUMBER: [RegexHandler(pattern='^\d+$', callback=round_number, pass_user_data=True)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling(poll_interval=2)
    # you can replace above line with commented below lines to use webhook instead of polling
    # updater.bot.set_webhook(url="{}{}".format(os.getenv('WEB_HOOK_DOMAIN', "https://testwebhook.bale.ai"),
    #                                           os.getenv('WEB_HOOK_PATH', "/get-upd")))
    # updater.start_webhook(listen=os.getenv('WEB_HOOK_IP', ""), port=int(os.getenv('WEB_HOOK_PORT', "")),
    #                       url_path=os.getenv('WEB_HOOK_PATH', ""))

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
