from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field


class ScoreEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    restaurant_name: str
    gmaps_link: str
    date_visited: date
    mood: float = 1.0  # 0.9‒1.1 step 0.1
    taste: int  # 0‒10
    experience: int  # 0‒10
    value: int  # 0‒10
    notes: Optional[str] = None
    final_score: float
    image_path_1: Optional[str] = None
    image_path_2: Optional[str] = None 