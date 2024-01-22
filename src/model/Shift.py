from src.model.Skill import Skill


class Shift:

    def __init__(self, name: str, needed_skills: list[Skill]):
        self.name = name
        self.needed_skills = needed_skills

    def __str__(self):
        return self.name
