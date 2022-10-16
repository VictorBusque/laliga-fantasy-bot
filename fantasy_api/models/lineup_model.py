import logging
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
    lastStats: Optional[List] = []
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

    def get_player_points(self) -> List[UserPlayer]:
        results = []
        players: List[UserPlayer] = []
        goalkeepers = [goalkeeper for goalkeeper in self.formation.goalkeeper
                        if goalkeeper.playerMaster.weekPoints != None]
        defenders = [defender for defender in self.formation.defender
                        if defender.playerMaster.weekPoints != None]
        midfielders = [midfielder for midfielder in self.formation.midfield
                        if midfielder.playerMaster.weekPoints != None]
        strikers = [striker for striker in self.formation.striker
                        if striker.playerMaster.weekPoints != None]
        results += goalkeepers
        results += defenders
        results += midfielders
        results += strikers
        results.sort(key = lambda p: p.playerMaster.weekPoints, reverse=True)
        return results
    
    def describe_points(self) -> List[str]:
        results = self.get_player_points()
        table_data = [player.__describe_week__() for player in results]
        if table_data:
            description = [f"En la jornada has conseguido *{self.points}* puntos."]
            description.append(markdownTable(table_data).setParams(row_sep = 'always', padding_width = 2, padding_weight = 'centerright').getMarkdown())
        else:
            description = ["Esta jornada tus jugadores no han puntuado."]
        return description
    
    def compare(self, previous_update=None) -> List[str]:
        if not previous_update:
            logging.warning("Previous update is Null, next time it'll work.")
            return None
        results = self.get_player_points()
        previous_results = previous_update.get_player_points()
        
        results = {player.playerMaster.id: player for player in results}
        previous_results = {player.playerMaster.id: player for player in previous_results}
        
        utterances = []
        for player_id, player in results.items():
            curr_player_points = player.playerMaster.weekPoints
            prev_player = previous_results.get(player_id)
            if prev_player:
                prev_player_points = previous_results.get(player_id).playerMaster.weekPoints
                if curr_player_points != prev_player_points:
                    diff = curr_player_points - prev_player_points
                    if diff > 0:
                        verb = "ganado"
                        emoji = "💪"
                    elif diff < 0: 
                        verb = "perdido"
                        emoji = "👎"
                    utterances.append(f"⚽ Actualización ⚽\n{player.playerMaster.nickname} ha {verb} {diff} puntos {emoji}. Tiene {curr_player_points} puntos.")
            else:
                utterances.append(f"⚽ Actualización ⚽\n{player.playerMaster.nickname} acaba de empezar a jugar el partido. Tiene {curr_player_points} puntos.")
        return utterances
            
