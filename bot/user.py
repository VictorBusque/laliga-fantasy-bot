import logging
from pydantic import BaseModel
from typing import Dict, List
from json import dump as jsond
from json import load as jsonl

DATABASE_FILE = "user_database.json"



class User(BaseModel):
    telegram_user_id: str=None
    team_id: str=None
    league_id: str=None
    bearer_token: str=None

    def save_or_update(self):
        try:
            with open(f"data/{DATABASE_FILE}", "r", encoding="utf8") as f:
                user_db = jsonl(f)
        except:
            logging.warning("There are no users on the DB yet. Creating first one.")
            user_db = {}
        user_db[self.telegram_user_id] = self.dict()
        with open(f"data/{DATABASE_FILE}", "w", encoding="utf8") as f:
            jsond(user_db, f, indent=4)
            
    @staticmethod
    def from_telegram_id(telegram_user_id: str):
        with open(f"data/{DATABASE_FILE}", "r", encoding="utf8") as f:
            user_db = jsonl(f)
            user = user_db.get(str(telegram_user_id))
            return User(**user)