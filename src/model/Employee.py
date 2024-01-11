from typing import List

from src.model.Skill import Skill


class Employee:

    def __init__(self, name: str, skills: List[Skill], is_shift_manager: bool = False):
        self.name = name
        self.skills = skills
        self.is_shift_manager = is_shift_manager

    def __str__(self):
        return self.name
