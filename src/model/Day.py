from typing import List

from src.model.Shift import Shift


class Day:

    def __init__(self, name: str, shifts: List[Shift]):
        self.name = name
        self.shifts = shifts

    def __str__(self):
        return self.name
