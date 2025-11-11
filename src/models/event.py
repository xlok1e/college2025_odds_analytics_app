from dataclasses import dataclass
from typing import List


@dataclass
class Coefficients:
    p1: float  
    x: float   
    p2: float  


@dataclass
class Event:
    id: int
    sport: str
    tournament: str
    country: str
    team1: str
    team2: str
    date: str
    records_count: int
    bookmakers: List[str]
    coefficients: Coefficients
