from src.model.Employee import Employee


class Team:

    def __init__(self, name: str, employees: list[Employee]):
        self.name = name
        self.employees = employees

    def __str__(self):
        return self.name
