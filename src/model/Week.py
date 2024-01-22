from src.model.Day import Day


class Week:

    def __init__(self, name: str, days: list[Day]):
        self.name = name
        self.days = days

    def __str__(self):
        return self.name
