from fantasy_api.models.player_model import FantasyPlayer
from fantasy_api.models.team_model import FantasyTeam
from typing import Dict, List

from utils.matching_utils import Utils

class FantasyDatabase:
    def __init__(self,
                player_data: Dict[str, FantasyPlayer]):
        self.player_data = player_data
        
    def get_players_from_team(self, team_id: str) -> List[FantasyPlayer]:
        players = list(self.player_data.values())
        team_players = [
            player for player in players if player.team.id == team_id
        ]
        return team_players
    
    def get_teams(self) -> List[FantasyTeam]:
        players = list(self.player_data.values())
        teams = []
        seen_ids = []
        for player in players:
            if player.team.id in seen_ids: 
                continue
            else:
                teams.append(player.team)
                seen_ids.append(player.team.id)
        return teams
    
    def get_team(self, team_id: str):
        teams = self.get_teams()
        for team in teams:
            if team.id == team_id:
                return team
        return None
    
    def get_players_from_team_and_position(self, team_id: str, positionId: str) -> List[FantasyPlayer]:
        team_players = self.get_players_from_team(team_id)
        team_position_players = [
            player for player in team_players if player.positionId == positionId
        ]
        return team_position_players
    
    def get_closest_teams(self, team_acronym_or_name: str=None, n: int=1, min_sim: int=0.75) -> List[FantasyTeam]:
        teams = self.get_teams()
        team_names = [(team.id, team.name.lower()) for team in teams]
        team_ids = Utils.find_closest_n(team_acronym_or_name, team_names, n)
        return [self.get_team(team_id) for team_id in team_ids]
    
    def get_closest_players(self, player_name: str, team_acronym_or_name: str=None, n: int=5, min_sim: int=0.75) -> List[FantasyPlayer]:
        player_name = player_name.lower()
        if team_acronym_or_name:
            team_acronym_or_name = team_acronym_or_name.lower()
        candidates = None
        if team_acronym_or_name:
            teams = self.get_closest_teams(team_acronym_or_name)
            if teams:
                selected_team = teams[0].id
                candidates = self.get_players_from_team(selected_team)
        if not candidates:
            candidates = list(self.player_data.values())
        candidate_names = [(candidate.id, candidate.nickname.lower()) for candidate in candidates]
        player_ids = Utils.find_closest_n(player_name, candidate_names, n)
        return [self.player_data[player_id] for player_id in player_ids]
        