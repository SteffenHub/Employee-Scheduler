import time
from typing import Dict, Union, List
from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import CpSolverSolutionCallback

from Excel_interface import write_to_excel
from RuleBuilder import add_every_shift_skill_is_assigned, add_one_employee_only_one_shift_per_day, \
    add_employee_cant_do_what_he_cant, add_employees_can_only_work_with_team_members, \
    add_one_employee_only_works_five_days_a_week, add_one_employee_works_the_same_shift_a_week, \
    add_every_employee_have_two_shift_pause, add_shift_cycle, add_at_least_one_shift_manager_per_team_per_day, \
    add_one_employee_only_works_five_days_in_a_row, add_an_employee_should_do_the_same_job_a_week, \
    add_employee_should_work_in_a_row, add_employee_should_work_night_shifts_in_a_row, \
    add_every_employee_should_do_same_amount_night_shifts

from model.Input_data_creator import create_input_data
from model.Team import Team
from model.Week import Week


class MySolutionPrinter(CpSolverSolutionCallback):
    def __init__(self, transitions: cp_model.IntVar, night_transitions: cp_model.IntVar, night_shift_distribution: cp_model.IntVar):
        CpSolverSolutionCallback.__init__(self)
        self.solution_count = 0
        self.start_time = time.time()
        self.transitions = transitions
        self.night_transitions = night_transitions
        self.night_shift_distribution = night_shift_distribution

    def on_solution_callback(self) -> None:
        print(
            f"Solution {self.solution_count}, "
            f"time = {time.time() - self.start_time} s, "
            f"objective = {self.ObjectiveValue()}, "
            f"transitions = {self.Value(self.transitions)}, "
            f"night_transitions = {self.Value(self.night_transitions)}, "
            f"night_shift_distribution = {self.Value(self.night_shift_distribution)}"
        )
        self.solution_count += 1


def get_model(model: cp_model.CpModel, all_vars: Dict[str, cp_model.IntVar], transitions: cp_model.IntVar,
              night_transitions: cp_model.IntVar, night_shift_distribution: cp_model.IntVar) -> Union[Dict[str, bool], None]:
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 8
    solver.parameters.max_time_in_seconds = 60.0
    solution_printer = MySolutionPrinter(transitions, night_transitions, night_shift_distribution)
    status = solver.Solve(model, solution_printer)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        if status == cp_model.OPTIMAL:
            print("Optimal")
        if status == cp_model.FEASIBLE:
            print("Feasible")
        return {var: solver.Value(all_vars[var]) == 1 for var in all_vars.keys()}
    else:
        if status == cp_model.INFEASIBLE:
            print("INFEASIBLE")
        if status == cp_model.UNKNOWN:
            print("UNKNOWN")
        return None


def main(weeks: List[Week], teams: List[Team]) -> Union[Dict[str, bool], None]:
    model = cp_model.CpModel()

    # create all vars
    all_vars: Dict[str, cp_model.IntVar] = {}
    for team in teams:
        for employee in team.employees:
            for week in weeks:
                for day in week.days:
                    for shift in day.shifts:
                        for needed_skill in shift.needed_skills:
                            key = f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"
                            var = model.NewBoolVar(key)
                            all_vars[key] = var

    # Hard constraints
    add_every_shift_skill_is_assigned(model, weeks, teams, all_vars)
    add_one_employee_only_one_shift_per_day(model, weeks, teams, all_vars)
    add_employee_cant_do_what_he_cant(model, weeks, teams, all_vars)
    add_employees_can_only_work_with_team_members(model, weeks, teams, all_vars)
    add_one_employee_only_works_five_days_a_week(model, weeks, teams, all_vars)
    add_one_employee_works_the_same_shift_a_week(model, weeks, teams, all_vars)
    add_every_employee_have_two_shift_pause(model, weeks, teams, all_vars)
    add_shift_cycle(model, weeks, teams, all_vars)
    add_at_least_one_shift_manager_per_team_per_day(model, weeks, teams, all_vars)
    add_one_employee_only_works_five_days_in_a_row(model, weeks, teams, all_vars)

    # Soft constrains
    minimize_var_work_in_row = add_employee_should_work_in_a_row(model, weeks, teams, all_vars, 3)
    minimize_var_work_in_row_at_night = add_employee_should_work_night_shifts_in_a_row(model, weeks, teams, all_vars, 7)
    minimize_var_same_night_shift_amount_per_employee = add_every_employee_should_do_same_amount_night_shifts(
        model, weeks, teams, all_vars, 2)
    # add_an_employee_should_do_the_same_job_a_week(model, weeks, teams, all_vars)
    model.Minimize(
        minimize_var_work_in_row +
        minimize_var_work_in_row_at_night +
        minimize_var_same_night_shift_amount_per_employee)
    print("All Rules added. Start Solver")
    model_result = get_model(model, all_vars, minimize_var_work_in_row, minimize_var_work_in_row_at_night, minimize_var_same_night_shift_amount_per_employee)
    if model_result is not None:
        write_to_excel(model_result, teams, weeks)
    return model_result


if __name__ == "__main__":
    weeks_input, teams_input = create_input_data()
    result = main(weeks_input, teams_input)
    print(result)
