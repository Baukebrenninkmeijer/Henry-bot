
#################################################
### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
#################################################
# file to edit: dev_nb/bot.ipynb

import re
import lib
import logging
import time
import pandas as pd
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
"""

api_token = lib.config['telegram']['api_token']

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class HenryBot:
    def __init__(self):
        self.db_conn = lib.DatabaseIO()
        self.triggers = self.db_conn.read_data('triggers')

    @staticmethod
    def start(update, context):
        """Send a message when the command /start is issued."""
        update.message.reply_text('Hi! I am HenryBot and you\'ve triggered me. You can add new triggers using /add. Get more information using /help')

    def update_triggers(self):
        self.db_conn.write_data(self.triggers, 'triggers')

    def add(self, update, context):
        try:
            value = update.message.text.split(' ', 1)[1]
            trigger, response = map(str.strip, value.split(':', 1))
            self.triggers.loc[trigger] = [response]
            update.message.reply_text(f'\'{trigger}\' added to the triggers')
            self.update_triggers()
        except IndexError:
            update.message.reply_text(f"No correctly formatted trigger found. Add a new trigger by typing /add <trigger>:<response>")

    def delete(self, update, context):
        try:
            trigger = update.message.text.split(' ', 1)[1]
            self.triggers = self.triggers.drop(trigger)
            update.message.reply_text(f'\'{trigger}\' deleted from triggers.')
            self.update_triggers()
        except IndexError:
            update.message.reply_text(f'Please add a trigger to remove. Format is /delete <trigger>')

    def get_triggers(self, update, context):
        # respond with only the triggers cause the responses give a message size error
        update.message.reply_text('\n'.join(self.triggers.index.tolist()))

    def triggered(self, update, context):
        """Echo the user message."""
        text = update.message.text
        user = update.message.from_user
        message = ''

        # Respond to 'I am'
        matches = re.search(r'ik ben (\w+)', text, re.I)
        if matches is not None:
            message += f'Hoi {matches.group(1)}, ik ben HenryBot\n'

        # Respond to added triggers
        for trigger, row in self.triggers.iterrows():
            regex = r'(\b|\A)\S{0,1}' + trigger + '\S{0,1}(\b){0,1}'
            if re.search(regex, text, re.I):
                assert isinstance(self.triggers.loc[trigger], pd.Series), f'Trigger query response is not a series. Likely duplicate trigger.'
                message += self.triggers.loc[trigger, 'response'] + '\n'

        message = message.format(user=user.first_name)
        if message:
            update.message.reply_text(message)

    @staticmethod
    def help(update, context):
        """Send a message when the command /help is issued."""
        update.message.reply_text('Help!')
        time.sleep(3)
        update.message.reply_text('Just kidding! HAHAHAHAHAHA')
        update.message.reply_text('''Add triggers by doing: /add <trigger>:<respons>
Remove triggers by doing: /delete <trigger>
Get all triggers by doing: /triggers\
        ''')


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    henry_bot = HenryBot()
    updater = Updater(api_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", henry_bot.start))
    dp.add_handler(CommandHandler("add", henry_bot.add))
    dp.add_handler(CommandHandler("delete", henry_bot.delete))
    dp.add_handler(CommandHandler("triggers", henry_bot.get_triggers))
    dp.add_handler(CommandHandler("help", henry_bot.help))

    # on noncommand i.e message - respond appropriately to the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, henry_bot.triggered))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
