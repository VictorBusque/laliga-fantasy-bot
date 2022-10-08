from bot.bot import bot
import logging
import locale

locale.setlocale(locale.LC_ALL, 'es_ES.utf8')

logger = logging.getLogger('__name__')
logging.basicConfig(level=logging.DEBUG)
logger.addHandler(logging.Formatter(fmt='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S'))
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    bot.infinity_polling()