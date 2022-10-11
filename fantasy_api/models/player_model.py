from pydantic import BaseModel
from enum import Enum
from fantasy_api.models.team_model import FantasyTeam
from typing import Dict, Optional
import locale
from markdownTable import markdownTable

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
        # return f"""
        # - Nombre: *{self.nickname}*
        # - Posición: {position_id_to_name.get(self.positionId)} 
        # - Equipo: {self.team.name}
        # - Valor de mercado: {locale.currency(int(self.marketValue), grouping=True)}
        # - Puntos temporada: {self.points} 
        # - Puntos por partido: {round(self.averagePoints, 2)}
        # """
        specs = [
            {
                "Dato": "Nombre",
                "Valor": self.nickname
            },
            {
                "Dato": "Posición",
                "Valor": position_id_to_name.get(self.positionId)
            },            {
                "Dato": "Equipo",
                "Valor": self.team.name
            },            {
                "Dato": "Valor de mercado",
                "Valor": locale.currency(int(self.marketValue), grouping=True)[:-5]+"€"
            },            {
                "Dato": "Puntos",
                "Valor": self.points
            },            {
                "Dato": "Puntos por partido",
                "Valor": round(self.averagePoints, 2)
            }
        ]
        if self.lastSeasonPoints:
            specs.append({"Dato": "Puntos temporada pasada",
                          "Valor": self.lastSeasonPoints})
        return markdownTable(specs).setParams(row_sep = 'always', padding_width = 2, padding_weight = 'centerright').getMarkdown()