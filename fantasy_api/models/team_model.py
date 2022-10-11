from typing import Optional
from pydantic import BaseModel, HttpUrl
from enum import Enum
import requests
from os import path, makedirs
from json import dump as jsond
from json import load as jsonl

class FantasyTeam(BaseModel):
    id: str
    name: str
    slug: str
    shortName: Optional[str]=None
    badgeColor: HttpUrl
    badgeGrey: Optional[HttpUrl]=None
    badgeWhite: HttpUrl
    
    def get_shortname(self):
        if self.shortName: 
            return self.shortName
        else:
            # Need to create the data folder the first time any request is executed.
            if not path.exists("data"):
                makedirs("data")
            elif not path.exists("data/teams_data_cache.json"):
                url = "https://api.laligafantasymarca.com/stats/v1/players/status?x-lang=es"
                response = requests.get(url)
                if response.ok:
                    team_data = response.json()
                    naming_map = {str(team.get("id")): team.get("shortName") for team in team_data}
                    with open("data/teams_data_cache.json", "w", encoding="utf8") as f:
                        jsond(naming_map, f, indent=4)
                else:
                    return "NULL"
            else:
                with open("data/teams_data_cache.json", "r", encoding="utf8") as f:
                    naming_map = jsonl(f)
            return naming_map[str(self.id)]
    