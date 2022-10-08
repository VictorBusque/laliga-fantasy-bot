from pydantic import BaseModel
from enum import Enum
from fantasy_api.models.team_model import FantasyTeam
from typing import Dict, Optional
import locale

class PositionId(str, Enum):
    Goalkeeper: str = "1"
    Defense: str = "2"
    Midfield: str = "3"
    Striker: str = "4"

position_id_to_name = {
    "1": "portero",
    "2": "defensa",
    "3": "centrocampista",
    "4": "delantero",
    "5": "entrenador"
}

class ImagesObject(BaseModel):
    big: Dict
    beat: Dict
    transparent: Dict

class FantasyPlayer(BaseModel):
    id: str
    images: ImagesObject
    positionId: str #PositionId
    nickname: str
    lastSeasonPoints: Optional[str]=None
    playerStatus: str
    marketValue: str
    team: FantasyTeam
    points: int
    averagePoints: float
    
    def __describe__(self) -> str:
        return f"""
        - Nombre: *{self.nickname}*
        - Posición: {position_id_to_name.get(self.positionId)} 
        - Equipo: {self.team.name}
        - Valor de mercado: {locale.currency(int(self.marketValue), grouping=True)}
        - Puntos temporada: {self.points} 
        - Puntos por partido: {round(self.averagePoints, 2)}
        """