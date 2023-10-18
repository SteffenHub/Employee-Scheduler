from typing import Dict, Union, List
from ortools.sat.python import cp_model
import random

from RuleBuilder import add_every_shift_skill_is_assigned
from src.model.Day import Day
from src.model.Employee import Employee
from src.model.Shift import Shift
from src.model.Skill import Skill


def get_model(model: cp_model.CpModel, all_vars: Dict[str, cp_model.IntVar]) -> Union[Dict[str, bool], None]:
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status == cp_model.OPTIMAL or cp_model.FEASIBLE:
        return {var: solver.Value(all_vars[var]) == 1 for var in all_vars}
    else:
        return None


def main(days: List[Day], employees: List[Employee]) -> Union[Dict[str, bool], None]:
    model = cp_model.CpModel()

    # create all vars
    all_vars: Dict[str, cp_model.IntVar] = {}
    for employee in employees:
        for day in days:
            for shift in day.shifts:
                for needed_skill in shift.needed_skills:
                    key = f"{day}_{shift}_{employee}_{needed_skill}"
                    var = model.NewBoolVar(key)
                    all_vars[key] = var

    # add rule every shift needs all skills
    add_every_shift_skill_is_assigned(model, days, employees, all_vars)
    return get_model(model, all_vars)


if __name__ == "__main__":
    # create Skills
    skills: List[Skill] = [Skill(f"Skill:{number}") for number in range(10)]

    # create Employee
    employees: List[Employee] = [Employee(f"Employee:{number}", random.sample(skills, random.randint(1, len(skills))))
                                 for
                                 number in range(5)]

    # create days and shifts
    days: List[Day] = []
    for day_number in range(7):
        days.append(
            Day(f"Day:{day_number}", [Shift(f"Shift:{number}", [random.choice(skills)]) for number in range(3)]))
    main(days, employees)
