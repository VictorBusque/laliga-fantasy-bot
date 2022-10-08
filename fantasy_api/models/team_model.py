from typing import Optional
from pydantic import BaseModel, HttpUrl
from enum import Enum

class FantasyTeam(BaseModel):
    id: str
    name: str
    slug: str
    shortName: Optional[str]=None
    badgeColor: HttpUrl
    badgeGrey: Optional[HttpUrl]=None
    badgeWhite: HttpUrl
    