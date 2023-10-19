from typing import Dict, Union, List
from ortools.sat.python import cp_model
from Excel_interface import write_to_excel
from RuleBuilder import add_every_shift_skill_is_assigned, add_one_employee_only_one_shift_per_day, \
    add_employee_cant_do_what_he_cant, add_employees_can_only_work_with_team_members, \
    add_one_employee_only_works_five_days_a_week, add_one_employee_works_the_same_shift_a_week, \
    add_every_employee_have_two_shift_pause, add_shift_cycle
from model.Input_data_creator import create_input_data
from model.Team import Team
from model.Week import Week


def get_model(model: cp_model.CpModel, all_vars: Dict[str, cp_model.IntVar]) -> Union[Dict[str, bool], None]:
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        return {var: solver.Value(all_vars[var]) == 1 for var in all_vars.keys()}
    else:
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

    add_every_shift_skill_is_assigned(model, weeks, teams, all_vars)
    add_one_employee_only_one_shift_per_day(model, weeks, teams, all_vars)
    add_employee_cant_do_what_he_cant(model, weeks, teams, all_vars)
    add_employees_can_only_work_with_team_members(model, weeks, teams, all_vars)
    add_one_employee_only_works_five_days_a_week(model, weeks, teams, all_vars)
    add_one_employee_works_the_same_shift_a_week(model, weeks, teams, all_vars)
    add_every_employee_have_two_shift_pause(model, weeks, teams, all_vars)
    add_shift_cycle(model, weeks, teams, all_vars)
    model_result = get_model(model, all_vars)
    if model_result is not None:
        write_to_excel(model_result, teams, weeks)
    return model_result


if __name__ == "__main__":
    weeks_input, teams_input = create_input_data()
    result = main(weeks_input, teams_input)
    print(result)
