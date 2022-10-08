from pydantic import BaseModel
from typing import Dict, List, Optional
from fantasy_api.models.player_model import ImagesObject
from fantasy_api.models.team_model import FantasyTeam
from markdownTable import markdownTable

class UserPlayerLastStat(BaseModel):
    stats: Dict
    weekNumber: int
    totalPoints: int

class UserPlayerMaster(BaseModel):
    points: int
    lastStats: List
    averagePoints: float
    images: ImagesObject
    id: str
    team: FantasyTeam
    name: str
    lastSeasonPoints: Optional[int]=None
    nickname: str
    positionId: int
    position: str
    marketValue: int
    playerStatus: Optional[str] = None
    weekPoints: Optional[int] = None

pos_to_acronym = {
    "Portero": "POR",
    "Defensa": "DEF",
    "Centrocampista": "CEN",
    "Delantero": "DEL",
    "Entrenador": "ENT"
}

class UserPlayer(BaseModel):
    playerMaster: UserPlayerMaster
    buyoutClause: int
    playerTeamId: str
    
    def __describe_week__(self):
        # return f"""- *{self.playerMaster.nickname}* [{self.playerMaster.position, self.playerMaster.team.name}] -> *{self.playerMaster.weekPoints}* puntos esta jornada."""
        return {
            "Jugador": self.playerMaster.nickname, 
            "Pos": pos_to_acronym.get(self.playerMaster.position), 
            "Equipo": self.playerMaster.team.shortName if self.playerMaster.team.shortName 
                        else self.playerMaster.team.name, 
            "Puntos": self.playerMaster.weekPoints
        }

class UserFormation(BaseModel):
    goalkeeper: List[UserPlayer]
    defender: List[UserPlayer]
    midfield: List[UserPlayer]
    striker: List[UserPlayer]
    coach: Optional[List[UserPlayer]]=None
    bench: Optional[List[UserPlayer]]=None
    tacticalFormation: List[int]

class UserTeam(BaseModel):
    id: str
    teamValue: int
    teamPoints: int

class UserLineup(BaseModel):
    formation: UserFormation
    points: int
    initialPoints: int
    teamSnapshotTookOn: str
    
    def describe_points(self):
        results = []
        players: List[UserPlayer] = []
        if self.formation.goalkeeper[0].playerMaster.weekPoints != None:
            players.append(self.formation.goalkeeper[0])
        defenders = [defender for defender in self.formation.defender
                        if defender.playerMaster.weekPoints != None]
        midfielders = [midfielder for midfielder in self.formation.midfield
                        if midfielder.playerMaster.weekPoints != None]
        strikers = [striker for striker in self.formation.striker
                        if striker.playerMaster.weekPoints != None]
        results += defenders
        results += midfielders
        results += strikers
        table_data = [player.__describe_week__() for player in results]
        print(table_data)
        description = [f"En lo que va de jornada llevas *{self.points}* puntos."]
        description.append(markdownTable(table_data).setParams(row_sep = 'always', padding_width = 2, padding_weight = 'centerright').getMarkdown())
        return description