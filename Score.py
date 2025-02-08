from datetime import timedelta
from sqlalchemy import Column, Integer, String
from Base import Base
from utils import format_time


# Define the model/table that stores username, score, and duration (in seconds)
class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True)  # Unique ID for each record
    username = Column(String, nullable=False)  # Username field
    difficulty = Column(String, nullable=False)  # Difficulty field
    score = Column(Integer, nullable=False)  # Score field
    duration_seconds = Column(
        Integer, nullable=False
    )  # Duration stored as total seconds

    def __repr__(self):
        return (
            f"<Score(username='{self.username}', difficulty='{self.difficulty}', score={self.score}, "
            f"duration='{self.duration_seconds}')>"
        )

    def to_dict(self):
        return {
            "username": self.username,
            "difficulty": self.difficulty,
            "score": self.score,
            "duration": format_time(self.duration_seconds),
        }
