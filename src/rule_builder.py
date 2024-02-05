from ortools.sat.python import cp_model

from ortools.sat.python.cp_model import IntVar

from src.model.Team import Team
from src.model.Week import Week


def add_every_shift_skill_is_assigned(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                      all_vars: dict[str, cp_model.IntVar]):
    for week in weeks:
        for day in week.days:
            for shift in day.shifts:
                for needed_skill in shift.needed_skills:
                    rule = [all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"] for team in teams for
                            employee in team.employees]
                    model.AddExactlyOne(rule)


def add_one_employee_only_one_shift_per_day(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                            all_vars: dict[str, cp_model.IntVar]):
    for team in teams:
        for employee in team.employees:
            for week in weeks:
                for day in week.days:
                    rule = [all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"] for shift in day.shifts
                            for
                            needed_skill in shift.needed_skills]
                    model.AddAtMostOne(rule)


def add_employee_cant_do_what_he_cant(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                      all_vars: dict[str, cp_model.IntVar]):
    for team in teams:
        for employee in team.employees:
            for week in weeks:
                for day in week.days:
                    for shift in day.shifts:
                        for needed_skill in shift.needed_skills:
                            if needed_skill not in employee.skills:
                                rule = all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"]
                                model.Add(rule == 0)


def add_employees_can_only_work_with_team_members(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                                  all_vars: dict[str, cp_model.IntVar]):
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


def add_one_employee_only_works_five_days_a_week(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                                 all_vars: dict[str, cp_model.IntVar]):
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


def add_one_employee_only_works_five_days_in_a_row(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                                   all_vars: dict[str, cp_model.IntVar]):
    period = {}
    i = 1
    for week in weeks:
        for day in week.days:
            period[i] = {"week": week, "day": day}
            i = i + 1

    for team in teams:
        for employee in team.employees:
            unique_index = 0
            for i in range(1, len(period) - 4):
                days_worked = []
                for j in range(i, i + 6):
                    [days_worked.append(
                        all_vars[f"{period[j]['week']}_{period[j]['day']}_{shift}_{team}_{employee}_{needed_skill}"])
                        for shift in period[j]['day'].shifts for needed_skill in shift.needed_skills]
                help_int = model.NewIntVar(0, 6, f"int_var_help_five_days_a_row_{team}_{employee}_{unique_index}")
                unique_index = unique_index + 1
                model.Add(help_int == sum(days_worked))
                model.Add(help_int <= 5)


def add_one_employee_works_max_seven_days_in_a_row(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                                   all_vars: dict[str, cp_model.IntVar]):
    period = {}
    i = 1
    for week in weeks:
        for day in week.days:
            period[i] = {"week": week, "day": day}
            i = i + 1

    for team in teams:
        for employee in team.employees:
            unique_index = 0
            for i in range(1, len(period) - 6):
                days_worked = []
                for j in range(i, i + 8):
                    [days_worked.append(
                        all_vars[f"{period[j]['week']}_{period[j]['day']}_{shift}_{team}_{employee}_{needed_skill}"])
                        for shift in period[j]['day'].shifts for needed_skill in shift.needed_skills]
                help_int = model.NewIntVar(0, 8, f"int_var_help_six_days_a_row_{team}_{employee}_{unique_index}")
                unique_index = unique_index + 1
                model.Add(help_int == sum(days_worked))
                model.Add(help_int <= 7)


def add_one_employee_works_the_same_shift_a_week(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                                 all_vars: dict[str, cp_model.IntVar]):
    unique_key = 1
    for week in weeks:
        for team in teams:
            for employee in team.employees:
                # keys = M, A, N. Every possible assignment for this employee in this week in shift M/A/N
                shift_vars: dict[str, list[cp_model.IntVar]] = {}
                for day in week.days:
                    for shift in day.shifts:
                        for needed_skill1 in shift.needed_skills:
                            shift_vars[str(shift)] = (
                                    [all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill1}"]] +
                                    shift_vars[str(shift)]) if str(shift) in shift_vars.keys() else [
                                all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill1}"]]
                for shift1 in shift_vars.keys():
                    for shift2 in shift_vars.keys():
                        if shift1 is not shift2:
                            help_var_bool = model.NewBoolVar(
                                f"bool_help_{shift1}_{week}_{team}_{employee}_{unique_key}")
                            help_var_int = model.NewIntVar(0, len(shift_vars[shift1]),
                                                           f"int_help_{shift1}_{week}_{team}_{employee}_{unique_key}")
                            unique_key = unique_key + 1
                            # if employee works at least ones a week in shift1 then he can't work in shift2 this week
                            model.Add(help_var_int == sum(shift_vars[shift1]))
                            model.Add(help_var_int >= 1).OnlyEnforceIf(help_var_bool)
                            model.Add(help_var_int < 1).OnlyEnforceIf(help_var_bool.Not())
                            model.AddBoolAnd([var.Not() for var in shift_vars[shift2]]).OnlyEnforceIf(help_var_bool)


def add_every_employee_have_two_shift_pause(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                            all_vars: dict[str, cp_model.IntVar]):
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


def add_shift_cycle(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                    all_vars: dict[str, cp_model.IntVar], shift_cycle: list[str]):
    for team in teams:
        for i in range(0, len(weeks) - 1):
            for shift in shift_cycle:
                help_bool_var = model.NewBoolVar(f"help_bool_shift_cycle_{team}_{weeks[i]}_{shift}")
                work_week_i_shift = [all_vars[f"{weeks[i]}_{day}_{x_shift}_{team}_{employee}_{needed_skill}"]
                                     for day in weeks[i].days
                                     for employee in team.employees
                                     for x_shift in day.shifts
                                     if x_shift.name == shift
                                     for needed_skill in x_shift.needed_skills]
                help_int_var = model.NewIntVar(0, len(work_week_i_shift),
                                               f"help_int_shift_cycle_{team}_{weeks[i]}_{shift}")
                # Add if employee worked at least ones in shift then he works in shift+1 next week
                model.Add(help_int_var == sum(work_week_i_shift))
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


def add_at_least_one_shift_manager_per_team_per_day(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                                    all_vars: dict[str, cp_model.IntVar]):
    for team in teams:
        shift_manager = [employee for employee in team.employees if employee.is_shift_manager]
        for week in weeks:
            for day in week.days:
                model.AddAtLeastOne([all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"]
                                     for employee in shift_manager
                                     for shift in day.shifts
                                     for needed_skill in shift.needed_skills])


def add_illness(model: cp_model.CpModel, weeks: list[Week], all_vars: dict[str, cp_model.IntVar],
                employee: str, ill_week_days: list[str]):
    team, employee = employee.split("_")
    for week_day in ill_week_days:
        ill_week, ill_day = week_day.split("_")
        for week in weeks:
            if week.name == ill_week:
                for day in week.days:
                    if day.name == ill_day:
                        for shift in day.shifts:
                            for needed_skill in shift.needed_skills:
                                model.Add(all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"] == 0)


def add_employee_should_work_in_a_row(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                      all_vars: dict[str, cp_model.IntVar],
                                      cost: int) -> tuple[IntVar, dict[str, IntVar]]:
    minimize_list = []
    sum_max_var = (len(weeks) * 7 * cost)
    transitions_cost_per_employee: dict[str, cp_model.IntVar] = {}
    for team in teams:
        for employee in team.employees:
            work_days = []
            for week in weeks:
                for day in week.days:
                    works = model.NewBoolVar(f"help_var_{team}_{employee}_works_on_{week}_{day}")
                    possible_assignments = [all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"]
                                            for shift in day.shifts
                                            for needed_skill in shift.needed_skills]
                    model.Add(sum(possible_assignments) > 0).OnlyEnforceIf(works)
                    model.Add(sum(possible_assignments) == 0).OnlyEnforceIf(works.Not())
                    work_days.append(works)
            transitions = []
            # create transition list
            for i in range(0, len(work_days) - 1):
                is_transition = model.NewBoolVar(f"help_bool_var_transition_{team}_{employee}_{i}_{i + 1}")
                model.Add(work_days[i] != work_days[i + 1]).OnlyEnforceIf(is_transition)
                model.Add(work_days[i] == work_days[i + 1]).OnlyEnforceIf(is_transition.Not())
                transitions.append(is_transition)
            # add one more transition if employee works on first Monday.
            # So it isn't better to work on first Monday to have fewer transitions
            transitions.append(work_days[0])
            transitions_sum = model.NewIntVar(0, sum_max_var, f"transition_sum_{team}_{employee}")
            model.Add(transitions_sum == sum(transitions) * cost)
            transitions_cost_per_employee[f"{team}:{employee}"] = transitions_sum
            transitions_mul = model.NewIntVar(0, sum_max_var ** 2, f"transition_mul_{team}_{employee}")
            model.AddMultiplicationEquality(transitions_mul, [transitions_sum, transitions_sum])
            minimize_list.append(transitions_mul)
    var_to_minimize = model.NewIntVar(0, (sum_max_var ** 2) * len([e for t in teams for e in t.employees]),
                                      f"minimize_sum_work_in_a_row")
    model.Add(var_to_minimize == sum(minimize_list))
    return var_to_minimize, transitions_cost_per_employee


def add_employee_should_work_night_shifts_in_a_row(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                                   all_vars: dict[str, cp_model.IntVar], cost: int,
                                                   night_shift_name: str) -> tuple[IntVar, dict[str, IntVar]]:
    minimize_list = []
    sum_max_var = (len(weeks) * 7 * cost)
    transitions_cost_per_employee: dict[str, cp_model.IntVar] = {}
    for team in teams:
        for employee in team.employees:
            work_days_at_night = []
            for week in weeks:
                for day in week.days:
                    works_in_night_shift = model.NewBoolVar(
                        f"help_var_{team}_{employee}_works_in_night_shift_on_{week}_{day}")
                    possible_night_assignments = [all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"]
                                                  for shift in day.shifts
                                                  if shift.name == night_shift_name
                                                  for needed_skill in shift.needed_skills]
                    model.Add(sum(possible_night_assignments) > 0).OnlyEnforceIf(works_in_night_shift)
                    model.Add(sum(possible_night_assignments) == 0).OnlyEnforceIf(works_in_night_shift.Not())
                    work_days_at_night.append(works_in_night_shift)
            transitions_night = []
            # create transition list
            for i in range(0, len(work_days_at_night) - 1):
                is_transition = model.NewBoolVar(
                    f"help_bool_var_transition_in_night_shift_{team}_{employee}_{i}_{i + 1}")
                model.Add(work_days_at_night[i] != work_days_at_night[i + 1]).OnlyEnforceIf(is_transition)
                model.Add(work_days_at_night[i] == work_days_at_night[i + 1]).OnlyEnforceIf(is_transition.Not())
                transitions_night.append(is_transition)
            # add one more transition if employee works on first Monday.
            # So it isn't better to work on first Monday to have fewer transitions
            transitions_night.append(work_days_at_night[0])
            transitions_sum = model.NewIntVar(0, sum_max_var, f"transition_sum_night_shifts_{team}_{employee}")
            model.Add(transitions_sum == sum(transitions_night) * cost)
            transitions_cost_per_employee[f"{team}:{employee}"] = transitions_sum
            transitions_mul = model.NewIntVar(0, sum_max_var ** 2, f"transition_mul_night_shift_{team}_{employee}")
            model.AddMultiplicationEquality(transitions_mul, [transitions_sum, transitions_sum])
            minimize_list.append(transitions_mul)
    var_to_minimize = model.NewIntVar(0, (sum_max_var ** 2) * len([e for t in teams for e in t.employees]),
                                      f"minimize_sum_work_in_a_row_night_shifts")
    model.Add(var_to_minimize == sum(minimize_list))
    return var_to_minimize, transitions_cost_per_employee


def add_an_employee_should_do_the_same_job_a_week(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                                  all_vars: dict[str, cp_model.IntVar]):
    maximize_list = []
    for week in weeks:
        for team in teams:
            for employee in team.employees:
                assignments: dict[str, list[cp_model.IntVar]] = {}
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
                    assignments_sum[skill] = model.NewIntVar(
                        0, 10000,
                        f"help_var_same_job_a_week_{week}_{team}_{employee}_{skill}")
                    model.Add(assignments_sum[skill] == sum(assignments[skill]))
                help_max_var = model.NewIntVar(0, 10000, f"help_var_same_job_a_week_max_var_{week}_{team}_{employee}")
                model.AddMaxEquality(help_max_var, list(assignments_sum.values()))
                help_max_var_mult = model.NewIntVar(0, 100000,
                                                    f"help_var_same_job_a_week_max_var_mult_{week}_{team}_{employee}")
                model.AddMultiplicationEquality(help_max_var_mult, [help_max_var, help_max_var])
                maximize_list.append(help_max_var_mult)
    model.Maximize(sum(maximize_list))


def add_every_employee_should_do_same_amount_night_shifts(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                                          all_vars: dict[str, cp_model.IntVar], cost: int,
                                                          night_shift_name: str) -> tuple[IntVar, dict[str, IntVar]]:
    night_shifts_per_employee_minimize_list: list[cp_model.IntVar] = []
    night_shift_cost_per_employee: dict[str, cp_model.IntVar] = {}
    max_minimize_value = 0
    for team in teams:
        for employee in team.employees:
            night_shift_assignments = [all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"]
                                       for week in weeks
                                       for day in week.days
                                       for shift in day.shifts if shift.name == night_shift_name
                                       for needed_skill in shift.needed_skills]
            night_shift_assignments_sum = model.NewIntVar(0, len(night_shift_assignments * cost),
                                                          f"help_same_night_shift_amount_sum_{team}_{employee}")
            model.Add(night_shift_assignments_sum == sum(night_shift_assignments) * cost)
            night_shift_cost_per_employee[f"{team}:{employee}"] = night_shift_assignments_sum
            night_shift_assignments_mul = model.NewIntVar(0, len(night_shift_assignments * cost) ** 2,
                                                          f"help_same_night_shift_amount_mul_{team}_{employee}")
            model.AddMultiplicationEquality(night_shift_assignments_mul,
                                            [night_shift_assignments_sum, night_shift_assignments_sum])
            max_minimize_value += len(night_shift_assignments * cost) ** 2
            night_shifts_per_employee_minimize_list.append(night_shift_assignments_mul)
    minimize_value = model.NewIntVar(0, max_minimize_value, f"minimize_value_for_same_night_shift_amount")
    model.Add(minimize_value == sum(night_shifts_per_employee_minimize_list))
    return minimize_value, night_shift_cost_per_employee


def add_one_employee_should_work_max_five_days_in_a_row(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                                        all_vars: dict[str, cp_model.IntVar], cost: int):
    period = {}
    i = 1
    for week in weeks:
        for day in week.days:
            period[i] = {"week": week, "day": day}
            i = i + 1
    minimize_list = []
    five_days_a_row_cost_per_employee: dict[str, cp_model.IntVar] = {}
    for team in teams:
        for employee in team.employees:
            unique_index = 0
            over_time = []
            for i in range(1, len(period) - 5, 2):
                days_worked = []
                for j in range(i, i + 7):
                    [days_worked.append(
                        all_vars[f"{period[j]['week']}_{period[j]['day']}_{shift}_{team}_{employee}_{needed_skill}"])
                        for shift in period[j]['day'].shifts for needed_skill in shift.needed_skills]
                help_int = model.NewIntVar(0, 7, f"int_var_help_should_work_six_days_a_row_{team}_{employee}_{unique_index}")
                unique_index = unique_index + 1
                model.Add(help_int == sum(days_worked))

                help_more_than_five = model.NewBoolVar(f"help_var_more_than_five_{team}_{employee}_{unique_index}")
                model.Add(help_int > 5).OnlyEnforceIf(help_more_than_five)
                model.Add(help_int <= 5).OnlyEnforceIf(help_more_than_five.Not())
                over_time_help = model.NewIntVar(0, 2, f"int_var_help_over_time_should_work_five_days_a_row_{team}_{employee}_{unique_index}")
                model.Add(over_time_help == 0).OnlyEnforceIf(help_more_than_five.Not())
                model.Add(over_time_help == help_int - 5).OnlyEnforceIf(help_more_than_five)
                over_time.append(over_time_help)

            five_days_a_row_sum = model.NewIntVar(0, cost * len(over_time), f"int_var_help_should_work_six_days_a_row_sum_{team}_{employee}_{unique_index}")
            model.Add(five_days_a_row_sum == cost * sum(over_time))
            five_days_a_row_cost_per_employee[f"{team}:{employee}"] = five_days_a_row_sum

            five_days_mul = model.NewIntVar(0, (cost * len(over_time)) ** 2, f"int_var_help_should_work_six_days_a_row_mul_{team}_{employee}_{unique_index}")
            model.AddMultiplicationEquality(five_days_mul, [five_days_a_row_sum, five_days_a_row_sum])
            minimize_list.append(five_days_mul)
    return sum(minimize_list), five_days_a_row_cost_per_employee
