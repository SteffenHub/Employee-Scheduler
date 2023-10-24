from ortools.sat.python import cp_model
from typing import Dict, List

from model.Team import Team
from model.Week import Week


def add_every_shift_skill_is_assigned(model: cp_model.CpModel, weeks: List[Week], teams: List[Team],
                                      all_vars: Dict[str, cp_model.IntVar]):
    for week in weeks:
        for day in week.days:
            for shift in day.shifts:
                for needed_skill in shift.needed_skills:
                    rule = [all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"] for team in teams for
                            employee in team.employees]
                    model.AddExactlyOne(rule)


def add_one_employee_only_one_shift_per_day(model: cp_model.CpModel, weeks: List[Week], teams: List[Team],
                                            all_vars: Dict[str, cp_model.IntVar]):
    for team in teams:
        for employee in team.employees:
            for week in weeks:
                for day in week.days:
                    rule = [all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"] for shift in day.shifts
                            for
                            needed_skill in shift.needed_skills]
                    model.AddAtMostOne(rule)


def add_employee_cant_do_what_he_cant(model: cp_model.CpModel, weeks: List[Week], teams: List[Team],
                                      all_vars: Dict[str, cp_model.IntVar]):
    for team in teams:
        for employee in team.employees:
            for week in weeks:
                for day in week.days:
                    for shift in day.shifts:
                        for needed_skill in shift.needed_skills:
                            if needed_skill not in employee.skills:
                                rule = all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"]
                                model.Add(rule == 0)


def add_employees_can_only_work_with_team_members(model: cp_model.CpModel, weeks: List[Week], teams: List[Team],
                                                  all_vars: Dict[str, cp_model.IntVar]):
    for i in range(0, len(teams)):
        for j in range(i + 1, len(teams)):
            for employee1 in teams[i].employees:
                for employee2 in teams[j].employees:
                    for week in weeks:
                        for day in week.days:
                            for shift in day.shifts:
                                for needed_skill1 in shift.needed_skills:
                                    for needed_skill2 in shift.needed_skills:
                                        rule1 = all_vars[
                                            f"{week}_{day}_{shift}_{teams[i]}_{employee1}_{needed_skill1}"].Not()
                                        rule2 = all_vars[
                                            f"{week}_{day}_{shift}_{teams[j]}_{employee2}_{needed_skill2}"].Not()
                                        model.AddBoolOr(rule1, rule2)


def add_one_employee_only_works_five_days_a_week(model: cp_model.CpModel, weeks: List[Week], teams: List[Team],
                                                 all_vars: Dict[str, cp_model.IntVar]):
    for team in teams:
        for employee in team.employees:
            for week in weeks:
                days_worked = model.NewIntVar(0, 7, f"{employee.name}_days_worked_in_{week}")
                model.Add(days_worked <= 5)
                model.Add(days_worked == sum([
                    all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"] for day in week.days for shift in
                    day.shifts for
                    needed_skill in shift.needed_skills
                ]))


def add_one_employee_works_the_same_shift_a_week(model: cp_model.CpModel, weeks: List[Week], teams: List[Team],
                                                 all_vars: Dict[str, cp_model.IntVar]):
    unique_key = 1
    for week in weeks:
        for team in teams:
            for employee in team.employees:
                shift_vars: Dict[str, List[cp_model.IntVar]] = {}
                for day in week.days:
                    for shift in day.shifts:
                        for needed_skill1 in shift.needed_skills:
                            shift_vars[str(shift)] = [all_vars[
                                                          f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill1}"]] + \
                                                     shift_vars[str(shift)] if str(shift) in shift_vars.keys() else [
                                all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill1}"]]
                for shift1 in shift_vars.keys():
                    for shift2 in shift_vars.keys():
                        if shift1 is not shift2:
                            help_var_bool = model.NewBoolVar(
                                f"bool_help_{shift1}_{week}_{team}_{employee}_{unique_key}")
                            help_var_int = model.NewIntVar(0, 10000,
                                                           f"int_help_{shift1}_{week}_{team}_{employee}_{unique_key}")
                            unique_key = unique_key + 1
                            model.Add(help_var_int == sum(shift_vars[shift1]))
                            model.Add(help_var_int >= 1).OnlyEnforceIf(help_var_bool)
                            model.Add(help_var_int < 1).OnlyEnforceIf(help_var_bool.Not())
                            model.AddBoolAnd([var.Not() for var in shift_vars[shift2]]).OnlyEnforceIf(help_var_bool)


def add_every_employee_have_two_shift_pause(model: cp_model.CpModel, weeks: List[Week], teams: List[Team],
                                            all_vars: Dict[str, cp_model.IntVar]):
    keys = []
    values = []
    for week in weeks:
        for day in week.days:
            for shift in day.shifts:
                keys.append(f"{week}_{day}_{shift}")
                values.append(shift.needed_skills)
    for team in teams:
        for employee in team.employees:
            for i in range(0, len(keys)):
                for j in range(i + 1, i + 3 if i + 3 < len(keys) else len(keys)):
                    index = j % len(keys)
                    for needed_skill1 in values[i]:
                        for needed_skill2 in values[index]:
                            rule1 = all_vars[f"{keys[index]}_{team}_{employee}_{needed_skill2}"]
                            rule2 = all_vars[f"{keys[i]}_{team}_{employee}_{needed_skill1}"]
                            model.Add(rule1 == 0).OnlyEnforceIf(rule2)


def add_shift_cycle(model: cp_model.CpModel, weeks: List[Week], teams: List[Team],
                    all_vars: Dict[str, cp_model.IntVar]):
    # Only works if every day in every week have the same shifts
    shift_cycle = ["F", "S", "N"]
    for team in teams:
        for i in range(0, len(weeks) - 1):
            for shift in shift_cycle:
                help_bool_var = model.NewBoolVar(f"help_bool_shift_cycle_{team}_{weeks[i]}_{shift}")
                help_int_var = model.NewIntVar(0, 10000, f"help_int_shift_cycle_{team}_{weeks[i]}_{shift}")
                model.Add(help_int_var == sum([all_vars[f"{weeks[i]}_{day}_{x_shift}_{team}_{employee}_{needed_skill}"]
                                               for day in weeks[i].days
                                               for employee in team.employees
                                               for x_shift in day.shifts
                                               if x_shift.name == shift
                                               for needed_skill in x_shift.needed_skills])
                          )
                model.Add(help_int_var > 0).OnlyEnforceIf(help_bool_var)
                model.Add(help_int_var == 0).OnlyEnforceIf(help_bool_var.Not())
                model.Add(sum([all_vars[f"{weeks[i + 1]}_{day}_{x_shift}_{team}_{employee}_{needed_skill}"]
                               for day in weeks[i + 1].days
                               for x_shift in day.shifts
                               if x_shift.name is not shift_cycle[
                                   (shift_cycle.index(shift) + 1) % len(shift_cycle)]
                               for needed_skill in x_shift.needed_skills
                               for employee in team.employees]
                              ) == 0
                          ).OnlyEnforceIf(help_bool_var)


def add_at_least_one_shift_manager_per_team_per_day(model: cp_model.CpModel, weeks: List[Week], teams: List[Team],
                                                    all_vars: Dict[str, cp_model.IntVar]):
    for team in teams:
        shift_manager = [employee for employee in team.employees if employee.is_shift_manager]
        for week in weeks:
            for day in week.days:
                model.AddAtLeastOne([all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"]
                                     for employee in shift_manager
                                     for shift in day.shifts
                                     for needed_skill in shift.needed_skills])


def add_an_employee_should_do_the_same_job_a_week(model: cp_model.CpModel, weeks: List[Week], teams: List[Team],
                                                  all_vars: Dict[str, cp_model.IntVar]):
    maximize_list = []
    for week in weeks:
        for team in teams:
            for employee in team.employees:
                assignments: dict[str, List[cp_model.IntVar]] = {}
                for day in week.days:
                    for shift in day.shifts:
                        for needed_skill in shift.needed_skills:
                            if str(needed_skill) not in assignments.keys():
                                assignments[str(needed_skill)] = [
                                    all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"]]
                            else:
                                assignments[str(needed_skill)].append(
                                    all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"])
                assignments_sum: dict[str, cp_model.IntVar] = {}
                for skill in assignments.keys():
                    assignments_sum[skill] = model.NewIntVar(0, 10000,
                                                             f"help_var_same_job_a_week_{week}_{team}_{employee}_{skill}")
                    model.Add(assignments_sum[skill] == sum(assignments[skill]))
                help_max_var = model.NewIntVar(0, 10000, f"help_var_same_job_a_week_max_var_{week}_{team}_{employee}")
                model.AddMaxEquality(help_max_var, list(assignments_sum.values()))
                help_max_var_mult = model.NewIntVar(0, 100000,
                                                    f"help_var_same_job_a_week_max_var_mult_{week}_{team}_{employee}")
                model.AddMultiplicationEquality(help_max_var_mult, [help_max_var, help_max_var])
                maximize_list.append(help_max_var_mult)
    model.Maximize(sum(maximize_list))
