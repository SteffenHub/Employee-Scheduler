from ortools.sat.python import cp_model


class ConsoleOutput:

    def __init__(self, column_name: str, data: dict[str, cp_model.IntVar], cost: int):
        if cost == 0:
            raise ValueError("Cost can't be 0")
        self.column_name: str = column_name
        self.data: dict[str, cp_model.IntVar] = data
        self.cost: int = cost

