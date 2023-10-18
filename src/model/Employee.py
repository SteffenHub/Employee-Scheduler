from typing import List

from model.Skill import Skill


class Employee:

    def __init__(self, name: str, skills: List[Skill]):
        self.name = name
        self.skills = skills

    def __str__(self):
        return self.name
