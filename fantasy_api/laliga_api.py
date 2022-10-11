import requests
from typing import List
from bot.user import User
from fantasy_api.models.lineup_model import UserLineup
from fantasy_api.models.player_model import FantasyPlayer
from os import path, getenv, makedirs
from json import load as jsonl
from json import dump as jsond
from datetime import datetime, timedelta
import logging

class LaLigaFantasyAPI(object):
    def __init__(self, bearer_token: str=None, user_team_id: str=None, user_league_id: str=None):
        self.players_url = "https://api.laligafantasymarca.com/api/v3/players?x-lang=es"
        self.cache_file = "players_data_cache.json"
        self.update_interval = timedelta(minutes=2)
        self.lineup_url = "https://api.laligafantasymarca.com/api/v3/teams/{0}/lineup/week/{1}?x-lang=es"
        self.curr_week_url = "https://api.laligafantasymarca.com/api/v3/week/current?x-lang=es"
        
    def collect_players(self):
        response = requests.get(self.players_url)
        if response.ok:
            return {player.get("id"): player for player in response.json()}
        
    def cache_players(self):
        data = self.collect_players()
        # Need to create the data folder the first time any request is executed.
        if not path.exists("data"):
            makedirs("data")
        with open(f"data/{self.cache_file}", "w", encoding="utf8") as f:
            jsond(data, f, indent=4)
        return data
    
    def get_cached_players(self):
        with open(f"data/{self.cache_file}", "r", encoding="utf8") as f:
            data = jsonl(f)
        return data
    
    def check_update_cache(self):
        file_path = f"data/{self.cache_file}"
        try:
            mod_time = datetime.fromtimestamp(path.getmtime(file_path))
            time_from_last_update = (datetime.now()-mod_time)
            logging.info(f"{time_from_last_update.total_seconds()} seconds from last cached update, from {mod_time}.")
            if time_from_last_update >= self.update_interval:
                # Update players cache
                data = self.cache_players()
            else:
                data = self.get_cached_players()
        except:
            data = self.cache_players()
            
        return data

    def get_all_players(self, use_cache: bool=True) -> List[FantasyPlayer]:
        if use_cache:
            data = self.check_update_cache()
        else:
            data = self.collect_players()
        return {id: FantasyPlayer(**player) for id, player in data.items()}
    
    def get_curr_week(self):
        response = requests.get(self.curr_week_url)
        if response.ok:
            return response.json().get('weekNumber')
    
    def get_week_results(self, user: User, week_num: int=None):
        if not week_num:
            week_num = self.get_curr_week()
        user_team_id = user.team_id
        curr_week_points_url = self.lineup_url.format(user_team_id, week_num)
        headers = {
            "Authorization": f"Bearer {user.bearer_token}"
        }
        response = requests.get(curr_week_points_url, headers=headers)
        if response.ok:
            api_data = response.json()
            user_lineup = UserLineup(**api_data)
            return user_lineup