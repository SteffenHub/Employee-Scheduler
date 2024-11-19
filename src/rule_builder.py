from ortools.sat.python import cp_model

from ortools.sat.python.cp_model import IntVar

from src.model.Team import Team
from src.model.Week import Week


def add_every_shift_skill_is_assigned(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                      all_vars: dict[str, cp_model.IntVar]):
    """
    Ensures that exactly one employee with a required skill is assigned to each shift within a week.

    Iterates over weeks, days, and shifts to enforce that each required skill for a shift is covered by exactly
    one employee from any of the teams specified. This is done by adding constraints to the given
    CpModel object.

    :param model: The CpModel instance where constraints are added.
    :type model: cp_model.CpModel
    :param weeks: A list of Week objects, each containing days and shifts.
    :type weeks: list[Week]
    :param teams: A list of Team objects, each containing employees.
    :type teams: list[Team]
    :param all_vars: A dictionary mapping a unique string identifier to an IntVar for each
                     employee-skill-shift assignment.
    :type all_vars: dict[str, cp_model.IntVar]
    :return: None
    :rtype: NoneType
    """
    for week in weeks:
        for day in week.days:
            for shift in day.shifts:
                for needed_skill in shift.needed_skills:
                    rule = [all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"] for team in teams for
                            employee in team.employees]
                    model.AddExactlyOne(rule)


def add_one_employee_only_one_shift_per_day(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                            all_vars: dict[str, cp_model.IntVar]):
    """
    Adds a constraint to the given CpModel that ensures each employee can only work one shift
    per day across multiple teams and weeks.

    Iterates over all teams and their employees for each week and day, and adds a constraint
    such that at most one shift is assigned to each employee per day.

    :param model: The constraint programming model to which the constraint will be added.
    :type model: cp_model.CpModel
    :param weeks: A list of week objects that contain the scheduling information.
    :type weeks: list[Week]
    :param teams: A list of team objects which contain the employees and their scheduling details.
    :type teams: list[Team]
    :param all_vars: A dictionary mapping variable names to their respective CpModel integer variables.
    :type all_vars: dict[str, cp_model.IntVar]
    :return: None
    :rtype: NoneType
    """
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
    """
    Adds a constraint to the model ensuring that employees are not assigned tasks requiring skills they do not possess.

    Iterates over all employees in all teams, and for each employee, it checks if they have fixed skills. For each week,
    day, and shift, it verifies whether the required skills for the shift are present in the employee's skill set. If
    the employee does not have a required skill, a constraint is added to the model that prevents the employee from
    being assigned to that shift for that skill.

    :param model: Constraint programming model to which the constraints are added.
    :type model: cp_model.CpModel
    :param weeks: List of week objects representing the schedule weeks.
    :type weeks: list[Week]
    :param teams: List of team objects containing employees and other team-specific information.
    :type teams: list[Team]
    :param all_vars: Dictionary mapping string identifiers to CpModel variables.
    :type all_vars: dict[str, cp_model.IntVar]
    :return: None
    :rtype: NoneType
    """
    for team in teams:
        for employee in team.employees:
            if employee.fixed_skills:
                for week in weeks:
                    for day in week.days:
                        for shift in day.shifts:
                            for needed_skill in shift.needed_skills:
                                if needed_skill not in employee.skills:
                                    rule = all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"]
                                    model.Add(rule == 0)


def add_employees_can_only_work_with_team_members(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                                  all_vars: dict[str, cp_model.IntVar]):
    """
    Adds constraints to the model ensuring that employees can only work with
    their own team members.

    Iterates through each team, each employee in the teams, and the
    corresponding weeks, days, shifts, and needed skills to apply the specific
    rules. The constraint ensures that an employee from one team should not be
    scheduled together with an employee from another team for the same shift.

    :param model: The constraint programming model to add the constraints to.
    :type model: cp_model.CpModel
    :param weeks: List of weeks containing days and shifts for scheduling.
    :type weeks: list[Week]
    :param teams: List of teams where each team contains employees.
    :type teams: list[Team]
    :param all_vars: Dictionary holding the variables representing each possible
                     shift allocation.
    :type all_vars: dict[str, cp_model.IntVar]
    :return: None
    :rtype: NoneType
    """
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
    """
    Ensures that all employees work no more than five days a week in the given scheduling model.

    For each employee in each team, a new variable is created to count the days worked in each week.
    Constraints are added to ensure that the number of days worked is restricted to a maximum of five
    and is equal to the sum of the corresponding scheduling variables indicating work on specific
    days, shifts, and needed skills.

    :param model: The CP-SAT model where scheduling constraints are added.
    :type model: cp_model.CpModel
    :param weeks: List of Week objects representing the weeks in the scheduling horizon.
    :type weeks: list[Week]
    :param teams: List of Team objects, each containing employees who need scheduling.
    :type teams: list[Team]
    :param all_vars: Dictionary of scheduling variables keyed by string descriptors of the format
                    "{week}_{day}_{shift}_{team}_{employee}_{needed_skill}".
    :type all_vars: dict[str, cp_model.IntVar]
    :return: None
    :rtype: NoneType
    """
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
    """
    Adds a constraint to the model ensuring that each employee works no more than five consecutive days.

    This function adds a specific constraint to the provided CpModel object, ensuring
    that each employee from any team does not exceed working five days in a row. It
    iterates over the given weeks and teams, creating necessary variables and constraints
    within the model.

    :param model: An instance of the CpModel to which the constraints will be added.
    :type model: cp_model.CpModel
    :param weeks: A list of Week objects representing the scheduling weeks.
    :type weeks: list[Week]
    :param teams: A list of Team objects containing employees and their schedules.
    :type teams: list[Team]
    :param all_vars: A dictionary mapping string keys to cp_model.IntVar objects representing
                     different scheduling variables.
    :type all_vars: dict[str, cp_model.IntVar]
    :return: None
    :rtype: NoneType
    """
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


def add_one_employee_works_max_ten_days_in_a_row(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                                   all_vars: dict[str, cp_model.IntVar]):
    """
    Ensures that each employee works no more than ten days consecutively over
    the given period.

    This function iterates through each employee's schedule and constructs
    variables to track the number of consecutive workdays. It then adds
    constraints to the model to enforce the rule that no employee works more
    than ten days in a row.

    :param model: The constraint programming model.
    :type model: cp_model.CpModel
    :param weeks: A list of Week objects representing the scheduling period.
    :type weeks: list[Week]
    :param teams: A list of Team objects where each team contains multiple employees.
    :type teams: list[Team]
    :param all_vars: A dictionary mapping string keys to IntVar variables representing
                    scheduling decisions.
    :type all_vars: dict[str, cp_model.IntVar]
    :return: None
    :rtype: NoneType
    """
    period = {}
    i = 1
    for week in weeks:
        for day in week.days:
            period[i] = {"week": week, "day": day}
            i = i + 1

    for team in teams:
        for employee in team.employees:
            unique_index = 0
            for i in range(1, len(period) - 9):
                days_worked = []
                for j in range(i, i + 11):
                    [days_worked.append(
                        all_vars[f"{period[j]['week']}_{period[j]['day']}_{shift}_{team}_{employee}_{needed_skill}"])
                        for shift in period[j]['day'].shifts for needed_skill in shift.needed_skills]
                help_int = model.NewIntVar(0, 11, f"int_var_help_six_days_a_row_{team}_{employee}_{unique_index}")
                unique_index = unique_index + 1
                model.Add(help_int == sum(days_worked))
                model.Add(help_int <= 10)


def add_one_employee_works_the_same_shift_a_week(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                                 all_vars: dict[str, cp_model.IntVar]):
    """
    Add constraints to the model ensuring that an employee works the same shift throughout a week and not multiple
    different shifts.

    For each week and team, iterate through all employees and ensure that if an employee works in any shift (morning,
    afternoon, night) during a week, they are restricted from working in any other shift in that same week.

    :param model: The constraint programming model instance being modified.
    :type model: cp_model.CpModel
    :param weeks: The list of week objects, each containing days and shifts information.
    :type weeks: list[Week]
    :param teams: The list of team objects, each consisting of employees with specific skills.
    :type teams: list[Team]
    :param all_vars: Dictionary mapping string keys to CP model integer variables, representing possible assignments.
    :type all_vars: dict[str, cp_model.IntVar]
    :return: This function does not return a value. It modifies the given model parameter directly.
    :rtype: None
    :rtype: NoneType
    """
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
    """
    This function adds constraints to a CP model ensuring that every employee has a two-shift pause between
    shifts that require different skills. Specifically, it iterates through all weeks, days, and shifts
    to generate keys for each shift, which are then used to access corresponding variables from a dictionary.
    For each employee in each team, the function ensures that if an employee is assigned to a shift requiring
    a specific skill, they cannot be assigned to a subsequent shift within two shifts that requires a different
    skill.

    :param model: The CP model to which the constraints will be added.
    :type model: cp_model.CpModel
    :param weeks: A list of Week objects representing the scheduling periods.
    :type weeks: list[Week]
    :param teams: A list of Team objects containing employees.
    :type teams: list[Team]
    :param all_vars: A dictionary mapping shift keys to CP model variables representing employee assignments.
    :type all_vars: dict[str, cp_model.IntVar]
    :return: None
    :rtype: NoneType
    """
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
                    # TODO the index with % needed? remove index replace with j
                    index = j % len(keys)
                    for needed_skill1 in values[i]:
                        for needed_skill2 in values[index]:
                            rule1 = all_vars[f"{keys[index]}_{team}_{employee}_{needed_skill2}"]
                            rule2 = all_vars[f"{keys[i]}_{team}_{employee}_{needed_skill1}"]
                            model.Add(rule1 == 0).OnlyEnforceIf(rule2)


def add_shift_cycle(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                    all_vars: dict[str, cp_model.IntVar], shift_cycle: list[str]):
    """
    Adds shift cycle constraints to the model ensuring that if an employee works a
    specific shift in a given week, they will work the next shift in the cycle in the
    following week.

    :param model: The constraint programming model to which the constraints are added.
    :type model: cp_model.CpModel
    :param weeks: A list of Week objects representing the schedule weeks.
    :type weeks: list[Week]
    :param teams: A list of Team objects representing the teams to schedule.
    :type teams: list[Team]
    :param all_vars: A dictionary mapping variable names to the corresponding
                     cp_model.IntVar objects.
    :type all_vars: dict[str, cp_model.IntVar]
    :param shift_cycle: A list representing the cyclic order of shifts.
    :type shift_cycle: list[str]
    :return: None
    :rtype: NoneType
    """
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
    """
    Adds constraints to the model ensuring that there is at least one shift manager per team, per
    day.

    Given a list of weeks, teams, and a dictionary of variables representing shifts and skills,
    the function iterates through each team and day in the given weeks. For each team, it finds
    the employees who are designated as shift managers and adds a constraint to the model ensuring
    that at least one shift manager is assigned per day for the required shifts and skills.

    :param model: The constraint programming model to which the constraints will be added.
    :type model: cp_model.CpModel
    :param weeks: List of Week objects representing the weeks to be scheduled.
    :type weeks: list[Week]
    :param teams: List of Team objects, each representing a team of employees.
    :type teams: list[Team]
    :param all_vars: Dictionary mapping variable names to cp_model.IntVar objects representing the
                     possible shifts and skills for each employee.
    :type all_vars: dict[str, cp_model.IntVar]
    :return: None
    :rtype: NoneType
    """
    for team in teams:
        shift_manager = [employee for employee in team.employees if employee.is_shift_manager]
        for week in weeks:
            for day in week.days:
                model.AddAtLeastOne([all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"]
                                     for employee in shift_manager
                                     for shift in day.shifts
                                     for needed_skill in shift.needed_skills])


def add_absence_manually(model: cp_model.CpModel, weeks: list[Week], all_vars: dict[str, cp_model.IntVar],
                employee: str, ill_week_days: list[str]):
    """
    This function adds a manual absence for an employee by setting the relevant model variables
    to indicate that the employee is unavailable for work on specified days due to illness.

    :param model: Constraint Programming model to be modified.
    :type model: cp_model.CpModel
    :param weeks: List of Week objects containing the schedule information.
    :type weeks: list[Week]
    :param all_vars: Dictionary with keys as variable names and values as CP model variables.
    :type all_vars: dict[str, cp_model.IntVar]
    :param employee: A unique identifier for the employee including team information.
    :type employee: str
    :param ill_week_days: List of days the employee is ill, formatted as 'week_day'.
    :type ill_week_days: list[str]
    :return: None
    :rtype: NoneType
    """
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
                        model.Add(all_vars[f"{week}_{day}_vac_{team}_{employee}_vac"] + all_vars[f"{week}_{day}_ill_{team}_{employee}_ill"] == 1)


def add_employee_should_work_in_a_row(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                      all_vars: dict[str, cp_model.IntVar],
                                      cost: int) -> tuple[IntVar, dict[str, IntVar]]:
    """
    Add constraints that minimize the number of days an employee should work in a row.

    This function creates constraints in the given CP-SAT model to ensure that employees do not work on many
    days consecutively. It calculates the number of transitions (days off between working days) and penalizes
    the schedule based on the number of such transitions.

    :param model: The constraint programming model.
    :type model: cp_model.CpModel
    :param weeks: List of weeks, where each week contains days with shifts.
    :type weeks: list[Week]
    :param teams: List of teams, where each team contains employees.
    :type teams: list[Team]
    :param all_vars: Dictionary containing the variables representing employees’ assignments.
    :type all_vars: dict[str, cp_model.IntVar]
    :param cost: The penalty cost for transitions between working and non-working days.
    :type cost: int
    :return: Tuple containing the variable to minimize and the dictionary of transition costs per employee.
    :rtype: tuple[cp_model.IntVar, dict[str, cp_model.IntVar]]
    """
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


def add_employee_works_night_shifts_in_a_row(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                                   all_vars: dict[str, cp_model.IntVar], night_shift_name: str):
    """
    Adds constraints to the CP model ensuring that employees do not work more than a specified
    number of consecutive night shifts.

    The function iterates through all teams, their employees, and the given weeks, creating
    boolean variables that indicate whether an employee works a night shift on a specific day.
    It enforces that the sum of transitions between night and non-night shifts does not exceed
    a specified limit.

    :param model: CP model to add constraints to
    :type model: cp_model.CpModel
    :param weeks: List of Week objects representing the scheduling period
    :type weeks: list[Week]
    :param teams: List of Team objects containing employee information
    :type teams: list[Team]
    :param all_vars: Dictionary mapping variable names to CP model integer variables
    :type all_vars: dict[str, cp_model.IntVar]
    :param night_shift_name: String representing the name of the night shift
    :type night_shift_name: str
    :rtype: None
    :rtype: NoneType
    """
    for team in teams:
        for employee in team.employees:
            for week in weeks:
                work_days_at_night = []
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
                model.Add(sum(transitions_night) <= 2)


def add_employee_should_work_night_shifts_in_a_row(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                                   all_vars: dict[str, cp_model.IntVar], cost: int,
                                                   night_shift_name: str) -> tuple[IntVar, dict[str, IntVar]]:
    """
    Applies constraints to the model to minimize the number of night shift
    transitions for employees. It constraints each employee to have minimal
    transitions between working and not working night shifts, and assigns
    a cost to these transitions.

    :param model: The CP-SAT model where constraints are added.
    :type model: cp_model.CpModel
    :param weeks: A list of weeks considered for scheduling.
    :type weeks: list[Week]
    :param teams: A list of teams involved in the scheduling.
    :type teams: list[Team]
    :param all_vars: A dictionary containing all variables representing
                     shifts and assignments.
    :type all_vars: dict[str, cp_model.IntVar]
    :param cost: The cost associated with each transition in night shifts.
    :type cost: int
    :param night_shift_name: The name of the night shift.
    :type night_shift_name: str
    :return: A tuple containing the variable to minimize (representing
             the summed cost of night shift transitions) and a dictionary
             mapping employees to their respective transition cost variables.
    :rtype: tuple[cp_model.IntVar, dict[str, cp_model.IntVar]]
    """
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
    """
    Adds constraints to the model ensuring that each employee in a team will perform the same job
    throughout a given week. This enhances the model's objective function to maximize the consistency
    of job assignments.

    This function operates over the given model, iterating through the weeks, teams, and employees
    to compile job assignments for each employee and applies constraints to ensure that an employee
    performs similar tasks throughout the week.

    :param model: instance of CpModel used to define the constraints and objective.
    :type model: cp_model.CpModel
    :param weeks: list containing the Week objects.
    :type weeks: list[Week]
    :param teams: list containing the Team objects.
    :type teams: list[Team]
    :param all_vars: dictionary mapping variable names to IntVar instances.
    :type all_vars: dict[str, cp_model.IntVar]
    :return: None
    :rtype: NoneType
    """
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
    """
    Adds constraints to the given CP model to ensure that every employee in each team should work
    approximately the same number of night shifts. The function also returns the total cost
    variable to minimize and a dictionary mapping each employee to their shift cost.

    :param model: The CP model to which constraints will be added.
    :type model: cp_model.CpModel
    :param weeks: A list of weeks, where each week contains days and each day contains shifts.
    :type weeks: list[Week]
    :param teams: A list of teams, where each team contains employees.
    :type teams: list[Team]
    :param all_vars: A dictionary containing all assignment variables.
    :type all_vars: dict[str, cp_model.IntVar]
    :param cost: The cost associated with each night shift.
    :type cost: int
    :param night_shift_name: The name of the night shift.
    :type night_shift_name: str
    :return: A tuple containing the minimized value variable and a dictionary of each employee's
             night shift cost.
    :rtype: tuple[IntVar, dict[str, IntVar]]
    """
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


def add_every_employee_should_do_same_amount_of_shifts(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                                          all_vars: dict[str, cp_model.IntVar], cost: int) -> tuple[IntVar, dict[str, IntVar]]:
    """
    Adds constraints to the model to ensure that every employee performs the same
    number of shifts and returns a variable representing the minimized value
    of the shift costs for each employee.

    Constraints are added to balance the number of shifts performed by employees
    in the given teams over the specified weeks, with each shift assignment
    multiplied by the provided cost. The function also creates auxiliary variables
    needed for the constraints and objective.

    :param model: The constraint programming model to which constraints are added
    :type model: cp_model.CpModel
    :param weeks: List of Week objects representing the schedule structure
    :type weeks: list[Week]
    :param teams: List of Team objects containing employees information
    :type teams: list[Team]
    :param all_vars: Dictionary of variables representing shift assignments
    :type all_vars: dict[str, cp_model.IntVar]
    :param cost: Cost multiplier for shift assignments
    :type cost: int
    :return: A tuple containing:
        - minimize_value (int): A variable representing the minimized value for balanced
          shift assignments.
        - shift_cost_per_employee (dict[str, int]): A dictionary mapping
          employee identifiers to their respective shift assignment cost variables.
    :rtype: tuple[IntVar, dict[str, IntVar]]
    """
    shifts_per_employee_minimize_list: list[cp_model.IntVar] = []
    shift_cost_per_employee: dict[str, cp_model.IntVar] = {}
    max_minimize_value = 0
    for team in teams:
        for employee in team.employees:
            shift_assignments = [all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"]
                                    for week in weeks
                                    for day in week.days
                                    for shift in day.shifts
                                    for needed_skill in shift.needed_skills]
            shift_assignments_sum = model.NewIntVar(0, len(shift_assignments * cost),f"help_same_shift_amount_sum_{team}_{employee}")
            model.Add(shift_assignments_sum == sum(shift_assignments) * cost)
            shift_cost_per_employee[f"{team}:{employee}"] = shift_assignments_sum
            shift_assignments_mul = model.NewIntVar(0, len(shift_assignments * cost) ** 2,
                                                          f"help_same_shift_amount_mul_{team}_{employee}")
            model.AddMultiplicationEquality(shift_assignments_mul,
                                            [shift_assignments_sum, shift_assignments_sum])
            max_minimize_value += len(shift_assignments * cost) ** 2
            shifts_per_employee_minimize_list.append(shift_assignments_mul)
    minimize_value = model.NewIntVar(0, max_minimize_value, f"minimize_value_for_same_shift_amount")
    model.Add(minimize_value == sum(shifts_per_employee_minimize_list))
    return minimize_value, shift_cost_per_employee


def add_one_employee_should_work_max_five_days_in_a_row(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                                        all_vars: dict[str, cp_model.IntVar], cost: int):
    """
    Adds a constraint to the CP-SAT model to ensure that an employee does not work more than five days in a row.
    The function computes additional costs if an employee works more than five consecutive days and adds these
    costs to the model's objective function to be minimized.

    :param model: The CP-SAT model instance from the Google OR-Tools library.
    :type model: cp_model.CpModel
    :param weeks: A list containing the scheduling weeks.
    :type weeks: list[Week]
    :param teams: A list containing team information, including employees.
    :type teams: list[Team]
    :param all_vars: A dictionary mapping strings to CP-SAT integer variables. These variables indicate whether
                     an employee is assigned to a particular shift on a particular day and week.
    :type all_vars: dict[str, cp_model.IntVar]
    :param cost: The penalty cost incurred if an employee works more than five consecutive days.
    :type cost: int
    :return: A tuple containing the sum of the minimization terms and a dictionary mapping employee identifiers
             to their respective penalty costs.
    :rtype: tuple[int, dict[str, cp_model.IntVar]]
    """
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


def add_one_employee_should_work_max_ten_days_in_a_row(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                                        all_vars: dict[str, cp_model.IntVar], cost: int):
    """
    Adds constraint to the model ensuring that each employee should work a maximum of ten consecutive days,
    and penalizes any violation of this constraint.

    This function iterates over all employees in the given teams, creates variables representing workdays
    and transitions between workdays, and calculates the penalty for each employee if they work more than
    ten consecutive days.

    :param model: The CP-SAT model to which the constraint will be added.
    :type model: cp_model.CpModel
    :param weeks: List of weeks for the scheduling period.
    :type weeks: list[Week]
    :param teams: List of teams which contain employees.
    :type teams: list[Team]
    :param all_vars: Dictionary of all existing variables in the model.
    :type all_vars: dict[str, cp_model.IntVar]
    :param cost: The cost penalty for each instance of violating the ten consecutive days constraint.
    :type cost: int
    :return: A tuple containing the sum of all penalty variables and a dictionary detailing the cost penalties
             per employee for ten consecutive days violations.
    :rtype: tuple[int, dict[str, list[cp_model.IntVar]]]
    """
    minimize_list = []
    ten_days_a_row_cost_per_employee: dict[str, list[cp_model.IntVar]] = {}
    # result = {}
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
            transitions.append(work_days[0])
            # create transition list
            for i in range(0, len(work_days) - 1):
                is_transition = model.NewBoolVar(f"help_bool_var_transition_{team}_{employee}_{i}_{i + 1}")
                model.Add(work_days[i] != work_days[i + 1]).OnlyEnforceIf(is_transition)
                model.Add(work_days[i] == work_days[i + 1]).OnlyEnforceIf(is_transition.Not())
                transitions.append(is_transition)
            # add one more transition if employee works on first Monday.
            # So it isn't better to work on first Monday to have fewer transitions

            works_in_row_enumerate = []
            for i, work in enumerate(work_days):
                enum_till_now = []
                for j in range(0, i+1):
                    enum_till_now.append(transitions[j])
                help_int = model.NewIntVar(0, 1000, f"int_var_help_wegweef_{team}_{employee}_{i}")
                model.Add(help_int == sum(enum_till_now)).OnlyEnforceIf(work)
                model.Add(help_int == 0).OnlyEnforceIf(work.Not())
                works_in_row_enumerate.append(help_int)

            overtime = []
            for i in range(1, len(transitions)):
                y = []
                for j in range(len(transitions)):
                    help_bool = model.NewBoolVar(f"help_bool_var_transition_{team}_{employee}_{i}_{j}")
                    model.Add(works_in_row_enumerate[j] == i).OnlyEnforceIf(help_bool)
                    model.Add(works_in_row_enumerate[j] != i).OnlyEnforceIf(help_bool.Not())
                    y.append(help_bool)
                overtime_int = model.NewIntVar(0, 10000, f"int_var_help_weergergweef_{team}_{employee}_{i}")
                higher_than_five = model.NewBoolVar(f"help_bool_var_transition_ergerger_{team}_{employee}_{i}")
                model.Add(sum(y) > 5).OnlyEnforceIf(higher_than_five)
                model.Add(sum(y) <= 5).OnlyEnforceIf(higher_than_five.Not())
                model.Add(overtime_int == sum(y) - 5).OnlyEnforceIf(higher_than_five)
                model.Add(overtime_int == 0). OnlyEnforceIf(higher_than_five.Not())
                overtime.append(overtime_int)
            # result[f"{employee}"] = (works_in_row_enumerate, transitions, work_days, x)
    # return result
            for i, row in enumerate(overtime):
                five_days_a_row_sum = model.NewIntVar(0, cost * len(transitions), f"int_var_help_should_work_ten_days_a_row_sum_{team}_{employee}_{i}")
                model.Add(five_days_a_row_sum == cost * row)
                if f"{team}:{employee}" not in ten_days_a_row_cost_per_employee.keys():
                    ten_days_a_row_cost_per_employee[f"{team}:{employee}"] = []
                ten_days_a_row_cost_per_employee[f"{team}:{employee}"].append(five_days_a_row_sum)
                five_days_mul = model.NewIntVar(0, (cost * len(transitions)) ** 2,
                                                f"int_var_help_should_work_ten_days_a_row_mul_{team}_{employee}_{i}")
                model.AddMultiplicationEquality(five_days_mul, [five_days_a_row_sum, five_days_a_row_sum])
                minimize_list.append(five_days_mul)
    return sum(minimize_list), ten_days_a_row_cost_per_employee



def add_vacations(model: cp_model.CpModel, weeks: list[Week], teams: list[Team], all_vars: dict[str, cp_model.IntVar], number_intervalls: int, number_vac_per_intervall: int):
    """
    Adds vacation constraints to the given model for each employee in each team.

    This function imposes constraints on the given model to ensure employees in the specified
    teams are assigned vacations according to the parameters provided. For each employee, if
    they are used at least once in work assignments, the vacations intervals are enforced.
    Otherwise, no vacation is assigned. Each employee's vacation is spread over the specified
    number of intervals, with each interval containing a fixed number of vacation periods.

    :param model: The constraint programming model being used.
    :type model: cp_model.CpModel
    :param weeks: List of weeks containing the days and shifts for the scheduling model.
    :type weeks: list[Week]
    :param teams: List of teams whose employees' vacations need to be scheduled.
    :type teams: list[Team]
    :param all_vars: A dictionary mapping variable names to the corresponding CP model variables.
    :type all_vars: dict[str, cp_model.IntVar]
    :param number_intervalls: The number of vacation intervals each employee should have.
    :type number_intervalls: int
    :param number_vac_per_intervall: The number of vacation periods within each interval.
    :type number_vac_per_intervall: int
    :return: None
    :rtype: NoneType
    """
    for team in teams:
        for employee in team.employees:
            used = model.NewBoolVar(f"help_{team}_{employee}_used")
            all_work_assignments = [all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"]
                                    for week in weeks for day in week.days
                                    for shift in day.shifts for needed_skill in shift.needed_skills]
            model.Add(sum(all_work_assignments) >= 1).OnlyEnforceIf(used)
            model.Add(sum(all_work_assignments) == 0).OnlyEnforceIf(used.Not())
            employee_vacation = []
            for week in weeks:
                for day in week.days:
                    employee_vacation.append(all_vars[f"{week}_{day}_vac_{team}_{employee}_vac"])
                    assignments_during_vac = [all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"]
                                              for shift in day.shifts for needed_skill in shift.needed_skills]
                    model.Add(sum(assignments_during_vac) == 0).OnlyEnforceIf(all_vars[f"{week}_{day}_vac_{team}_{employee}_vac"])

            model.Add(sum(employee_vacation) == number_intervalls * number_vac_per_intervall).OnlyEnforceIf(used)
            model.Add(sum(employee_vacation) == 0).OnlyEnforceIf(used.Not())
            vac_starts = []
            for i, vac in enumerate(employee_vacation[:-number_vac_per_intervall]):
                vac_starts.append(model.NewBoolVar(f"vacation_starts_{i}_{team}_{employee}"))
            for i, vac in enumerate(vac_starts):
                for j in range(i, i + number_vac_per_intervall):
                    if i != j and j < len(vac_starts):
                        model.Add(vac_starts[j] == 0).OnlyEnforceIf(vac_starts[i])
                    model.Add(employee_vacation[j] == 1).OnlyEnforceIf(vac_starts[i])
            model.Add(sum(vac_starts) == number_intervalls).OnlyEnforceIf(used)
            model.Add(sum(vac_starts) == 0).OnlyEnforceIf(used.Not())


def add_illness(model: cp_model.CpModel, weeks: list[Week], teams: list[Team], all_vars: dict[str, cp_model.IntVar], number_intervalls: int, number_ill_per_intervall: int):
    """
    Add constraints to a CP model to simulate and manage employee illness over a
    certain number of intervals. This function ensures that employees are marked as
    ill during specific periods and that they are not assigned to any shifts during
    those periods.

    :param model: The CP model to which the constraints are added
    :type model: cp_model.CpModel
    :param weeks: A list of weeks to be considered for the schedule
    :type weeks: list[Week]
    :param teams: A list of teams, each containing employees
    :type teams: list[Team]
    :param all_vars: A dictionary of all CP variables used in the model
    :type all_vars: dict[str, cp_model.IntVar]
    :param number_intervalls: The number of intervals for illness periods
    :type number_intervalls: int
    :param number_ill_per_intervall: The number of illness days per interval
    :type number_ill_per_intervall: int
    :return: None
    :rtype: NoneType
    """
    for team in teams:
        for employee in team.employees:
            used = model.NewBoolVar(f"help_{team}_{employee}_used")
            all_work_assignments = [all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"]
                                    for week in weeks for day in week.days
                                    for shift in day.shifts for needed_skill in shift.needed_skills]
            model.Add(sum(all_work_assignments) >= 1).OnlyEnforceIf(used)
            model.Add(sum(all_work_assignments) == 0).OnlyEnforceIf(used.Not())
            employee_illness = []
            for week in weeks:
                for day in week.days:
                    employee_illness.append(all_vars[f"{week}_{day}_ill_{team}_{employee}_ill"])
                    assignments_during_ill = [all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"]
                                              for shift in day.shifts for needed_skill in shift.needed_skills]
                    model.Add(sum(assignments_during_ill) == 0).OnlyEnforceIf(all_vars[f"{week}_{day}_ill_{team}_{employee}_ill"])
            model.Add(sum(employee_illness) == number_intervalls * number_ill_per_intervall).OnlyEnforceIf(used)
            model.Add(sum(employee_illness) == 0).OnlyEnforceIf(used.Not())
            ill_starts = []
            for i, vac in enumerate(employee_illness[:-number_ill_per_intervall]):
                ill_starts.append(model.NewBoolVar(f"vacation_starts_{i}_{team}_{employee}"))
            for i, vac in enumerate(ill_starts):
                for j in range(i, i + number_ill_per_intervall):
                    if i != j and j < len(ill_starts):
                        model.Add(ill_starts[j] == 0).OnlyEnforceIf(ill_starts[i])
                    model.Add(employee_illness[j] == 1).OnlyEnforceIf(ill_starts[i])
            model.Add(sum(ill_starts) == number_intervalls).OnlyEnforceIf(used)
            model.Add(sum(ill_starts) == 0).OnlyEnforceIf(used.Not())

def add_vac_not_in_ill(model: cp_model.CpModel, weeks: list[Week], teams: list[Team], all_vars: dict[str, cp_model.IntVar]):
    """
    Adds constraints to the model ensuring that an employee cannot be on
    vacation and ill on the same day.

    :param model: The constraint programming model to which the constraints
                  are added.
    :type model: cp_model.CpModel
    :param weeks: A list of Week objects representing the weeks in the schedule.
    :type weeks: list[Week]
    :param teams: A list of Team objects representing the teams in the organization.
    :type teams: list[Team]
    :param all_vars: A dictionary of variables used in the model, indexed by
                     strings representing their names.
    :type all_vars: dict[str, cp_model.IntVar]
    :return: None
    :rtype: NoneType
    """
    for team in teams:
        for employee in team.employees:
            for week in weeks:
                for day in week.days:
                    model.Add(all_vars[f"{week}_{day}_ill_{team}_{employee}_ill"] + all_vars[f"{week}_{day}_vac_{team}_{employee}_vac"] <= 1)


def add_minimize_needed_skills(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                                        all_vars: dict[str, cp_model.IntVar], cost: int) \
        -> tuple[dict[str, dict[str, cp_model.BoolVar]], cp_model.IntVar]:
    """
    Adds constraints to minimize the number of needed skills per employee and returns a
    dictionary mapping employees' skills and a variable representing the total number of
    minimization terms.

    :param model: The constraint programming model.
    :type model: cp_model.CpModel
    :param weeks: List of weeks in the scheduling period.
    :type weeks: list[Week]
    :param teams: List of teams to consider.
    :type teams: list[Team]
    :param all_vars: Dictionary mapping variable names to their corresponding CP model
                     integer variables.
    :type all_vars: dict[str, cp_model.IntVar]
    :param cost: Cost associated with a shift without all needed skills.
    :type cost: int
    :return: A dictionary with employees and their skills and an integer variable
             representing the sum of skills minimization.
    :rtype: tuple[dict[str, dict[str, cp_model.BoolVar]], cp_model.IntVar]
    """
    skills_employee: dict[str, dict[str, cp_model.IntVar]] = {}
    for team in teams:
        for employee in team.employees:
            empl_skills: dict[str, list[cp_model.IntVar]] = {}
            for week in weeks:
                for day in week.days:
                    for shift in day.shifts:
                        for needed_skill in shift.needed_skills:
                            if str(needed_skill) not in empl_skills.keys():
                                empl_skills[str(needed_skill)] = [all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"]]
                            else:
                                empl_skills[str(needed_skill)].append(all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"])
            for skill_name, skills in empl_skills.items():
                int_var = model.NewIntVar(0, len(skills), f"help_var_minimize_needed_skills_{team}_{employee}_{skills}")
                model.Add(int_var == sum(skills))
                has_skill = model.NewBoolVar(f"help_var_has_skill_{team}_{employee}_{skill_name}")
                model.Add(int_var > 0).OnlyEnforceIf(has_skill)
                model.Add(int_var == 0).OnlyEnforceIf(has_skill.Not())
                if f"{team}_{employee}" not in skills_employee.keys():
                    skills_employee[f"{team}_{employee}"] = {}
                skills_employee[f"{team}_{employee}"][skill_name] = has_skill
            true_var = model.NewBoolVar(f"TRUE_VAR")
            model.Add(true_var == 1)
            if employee.fixed_skills:
                for skill in employee.skills:
                    skills_employee[f"{team}_{employee}"][str(skill)] = true_var
    minimize_list = []
    for team, employee_skills in skills_employee.items():
        for skill, has_skill in employee_skills.items():
            minimize_list.append(has_skill)
    return skills_employee, sum(minimize_list)


def add_minimize_needed_employees(model: cp_model.CpModel, weeks: list[Week], teams: list[Team],
                                  all_vars: dict[str, cp_model.IntVar], cost: int) -> cp_model.LinearExpression:
    """
    Adds constraints to the model to minimize the number of needed employees who do not have fixed
    skills by creating a sum of boolean variables, indicating whether each employee is needed for any
    of the shifts. The cost associated with needing an employee is multiplied by the boolean variable
    and added to a minimization list. The sum of the minimization list is returned.

    :param model: The constraint programming model to which constraints are added.
    :type model: cp_model.CpModel
    :param weeks: A list of Week objects representing the scheduling weeks.
    :type weeks: list[Week]
    :param teams: A list of Team objects, each containing a list of employees.
    :type teams: list[Team]
    :param all_vars: A dictionary mapping variable names to their corresponding cp_model.IntVar objects.
    :type all_vars: dict[str, cp_model.IntVar]
    :param cost: The cost associated with needing an employee.
    :type cost: int
    :return: The sum of the minimized boolean expression indicating the number of needed employees.
    :rtype: cp_model.LinearExpression
    """
    minimize_list = []
    for team in teams:
        for employee in team.employees:
            if employee.fixed_skills:
                continue
            needed_times = [
                all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}"]
                for week in weeks
                for day in week.days
                for shift in day.shifts
                for needed_skill in shift.needed_skills
                      ]
            needed = model.NewBoolVar(f"help_var_needed_{team}_{employee}")
            model.Add(sum(needed_times) > 0).OnlyEnforceIf(needed)
            model.Add(sum(needed_times) == 0).OnlyEnforceIf(needed.Not())
            minimize_list.append(needed * cost)
    return sum(minimize_list)
