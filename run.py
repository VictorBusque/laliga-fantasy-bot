from bot.bot import bot
import logging
import locale
from telebot.types import BotCommand
from fantasy_api.laliga_api import LaLigaFantasyAPI
import json


locale.setlocale(locale.LC_ALL, 'es_ES.utf8')

logger = logging.getLogger('__name__')
logging.basicConfig(level=logging.DEBUG)
logger.addHandler(logging.Formatter(fmt='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S'))
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    player_data = LaLigaFantasyAPI().cache_players()
    
    try:
        with open("config/commands.json", "r", encoding="utf8") as f:
            commands = json.load(f)
            base_commands = [
                BotCommand(comm["command"], comm["description"]) for comm in commands
            ]
    except:
        base_commands = []
    player_commands = []
    player_data = list(player_data.values())
    player_data.sort(key = lambda p: p.get("points"))
    for player in player_data:
        player_commands.append(BotCommand(f"p{player.get('id')}", f"Info de {player.get('nickname')}"))
    commands = (base_commands + player_commands)[:100]
    print(len(commands))
    bot.set_my_commands(
        commands
    )
    bot.infinity_polling()