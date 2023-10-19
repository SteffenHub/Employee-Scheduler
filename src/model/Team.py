from typing import List

from model.Employee import Employee


class Team:

    def __init__(self, name: str, employees: List[Employee]):
        self.name = name
        self.employees = employees

    def __str__(self):
        return self.name
