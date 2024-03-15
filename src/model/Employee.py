from typing import List

from src.model.Skill import Skill


class Employee:

    def __init__(self, name: str, skills: list[Skill], is_shift_manager: bool = False, fixed_skills: bool = True):
        self.name = name
        self.skills = skills
        self.is_shift_manager = is_shift_manager
        self.fixed_skills = fixed_skills

    def __str__(self):
        return self.name
