from ortools.sat.python import cp_model
from typing import Dict, Union, List
from src.model.Day import Day
from src.model.Employee import Employee
from src.model.Shift import Shift
from src.model.Skill import Skill


def add_every_shift_skill_is_assigned(model: cp_model.CpModel, days: List[Day], employees: List[Employee],
                                      all_vars: Dict[str, cp_model.IntVar]):
    for day in days:
        for shift in day.shifts:
            for needed_skill in shift.needed_skills:
                model.AddBoolXOr(
                    [all_vars[f"{day}_{shift}_{employee}_{needed_skill}"] for employee in employees if
                     needed_skill in employee.skills])