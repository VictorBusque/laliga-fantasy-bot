from time import sleep
from bot.bot import bot
import logging
import locale
from telebot.types import BotCommand
from fantasy_api.laliga_api import LaLigaFantasyAPI
import json
from bot.user import User
from threading import Thread

locale.setlocale(locale.LC_ALL, 'es_ES.utf8')

logger = logging.getLogger('__name__')
logging.basicConfig(level=logging.DEBUG)
logger.addHandler(logging.Formatter(fmt='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S'))
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

UPDATE_INTERVAL = 30

def main_thread():
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
    player_data.sort(key = lambda p: p.get("points"), reverse=True)
    for player in player_data:
        player_commands.append(BotCommand(f"p{player.get('id')}", f"Info de {player.get('nickname')}"))
    commands = (base_commands + player_commands)[:100]
    logging.info(f"Loading {len(commands)} commands")
    logging.info([(comm.command, comm.description) for comm in commands])
    bot.set_my_commands(
        commands
    )
    bot.infinity_polling()
    
def notification_thread():
    laliga_api = LaLigaFantasyAPI()
    while True:
        users = User.load_users()
        curr_week = laliga_api.get_curr_week()
        for user in users:
            if not user.live_updates_active:
                continue
            else:
                logging.info(f"Checking updates on user: {user.telegram_user_id}")
                curr_lineup = laliga_api.get_week_results(user)
                if user.last_update_week == curr_week:
                    prev_lineup = user.last_update
                    updates = curr_lineup.compare(prev_lineup)
                    user.last_update = curr_lineup
                    user.save_or_update()
                    for update in updates:
                        bot.send_message(user.telegram_user_id, update)
                else:
                    # New week, updating user's internal thing and notifying updates.
                    user.last_update = curr_lineup
                    user.last_update_week = curr_week
                    user.save_or_update()
        sleep(UPDATE_INTERVAL)
                
            


if __name__ == "__main__":
    notification_thread = Thread(target=notification_thread)
    notification_thread.start()
    main_thread()
