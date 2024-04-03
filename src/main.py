import time
from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import CpSolverSolutionCallback
from prettytable import PrettyTable

from src.excel_interface import write_to_excel, read_from_excel
from src.rule_builder import (add_every_shift_skill_is_assigned, add_one_employee_only_one_shift_per_day,
                              add_employee_cant_do_what_he_cant, add_employees_can_only_work_with_team_members,
                              add_one_employee_only_works_five_days_a_week,
                              add_one_employee_works_the_same_shift_a_week,
                              add_every_employee_have_two_shift_pause, add_shift_cycle,
                              add_at_least_one_shift_manager_per_team_per_day,
                              add_one_employee_only_works_five_days_in_a_row, add_employee_should_work_in_a_row,
                              add_employee_should_work_night_shifts_in_a_row,
                              add_every_employee_should_do_same_amount_night_shifts, add_illness,
                              add_one_employee_should_work_max_five_days_in_a_row, add_vacations,
                              add_one_employee_works_max_ten_days_in_a_row,
                              add_one_employee_should_work_max_ten_days_in_a_row,
                              add_every_employee_should_do_same_amount_of_shifts,
                              add_vac_not_in_ill, add_absence_manually, add_employee_works_night_shifts_in_a_row,
                              add_minimize_needed_skills, add_minimize_needed_employees)

from model.Input_data_creator import get_teams_input_data, get_weeks_input_data
from model.Team import Team
from model.Week import Week


class MySolutionPrinter(CpSolverSolutionCallback):
    def __init__(self, transition_cost: dict[str, cp_model.IntVar], night_transitions: dict[str, cp_model.IntVar],
                 night_shift_distribution: dict[str, cp_model.IntVar], shift_distribution: dict[str, cp_model.IntVar], ten_days_a_row: dict[str, list[cp_model.IntVar]], all_vars):
        CpSolverSolutionCallback.__init__(self)
        self.solution_count = 0
        self.start_time = time.time()
        self.transition_cost = transition_cost
        self.night_transitions = night_transitions
        self.night_shift_distribution = night_shift_distribution
        self.shift_distribution = shift_distribution
        self.ten_days_a_row = ten_days_a_row
        self.all_vars = all_vars

    def on_solution_callback(self) -> None:
        table = PrettyTable()
        table.field_names = ["Team", "Employee", "transitions", "transition_cost", "night_transitions",
                             "night_transitions_cost", "night_shift_distribution", "night_shift_distribution cost",
                             "shift_distribution", "shift_distribution cost",
                             "ten_days_a_row", "ten_days_a_row_cost", "sum_costs"]

        print(f"Solution {self.solution_count}, time {time.time() - self.start_time}s")
        transitions_sum = 0
        transitions_cost_sum = 0
        night_transition_sum = 0
        night_transitions_cost_sum = 0
        night_shift_distribution_sum = 0
        night_shift_distribution_cost_sum = 0
        shift_distribution_sum = 0
        shift_distribution_cost_sum = 0
        ten_days_a_row_sum = 0
        ten_days_a_row_cost_sum = 0
        for i, teamEmployee in enumerate(self.transition_cost.keys()):
            team, employee = teamEmployee.split(":")
            next_team = list(self.transition_cost.keys())[i+1].split(":")[0] if i < len(self.transition_cost)-1 else team
            transitions = int(self.Value(self.transition_cost[teamEmployee]) / 3)
            transitions_sum += transitions
            transitions_cost = self.Value(self.transition_cost[teamEmployee]) ** 2
            transitions_cost_sum += transitions_cost
            night_transitions = int(self.Value(self.night_transitions[teamEmployee]) / 7)
            night_transition_sum += night_transitions
            night_transitions_cost = self.Value(self.night_transitions[teamEmployee]) ** 2
            night_transitions_cost_sum += night_transitions_cost

            night_shift_distribution = int(self.Value(self.night_shift_distribution[teamEmployee]) / 7)
            night_shift_distribution_sum += night_shift_distribution
            night_shift_distribution_cost = self.Value(self.night_shift_distribution[teamEmployee]) ** 2
            night_shift_distribution_cost_sum += night_shift_distribution_cost
            # TODO durch richtige zahl dividieren
            shift_distribution = int(self.Value(self.shift_distribution[teamEmployee]) / 3)
            shift_distribution_sum += shift_distribution
            shift_distribution_cost = self.Value(self.shift_distribution[teamEmployee]) ** 2
            shift_distribution_cost_sum += shift_distribution_cost

            ten_days_a_row = [int(self.Value(x) / 10000) for x in self.ten_days_a_row[teamEmployee]]
            for j in range(len(ten_days_a_row)):
                ten_days_a_row_sum += ten_days_a_row[j]
            ten_days_a_row_cost_list = [self.Value(x) ** 2 for x in self.ten_days_a_row[teamEmployee]]
            ten_days_a_row_cost = 0
            for j in range(len(ten_days_a_row_cost_list)):
                ten_days_a_row_cost_sum += ten_days_a_row_cost_list[j]
                ten_days_a_row_cost += ten_days_a_row_cost_list[j]
            sum_costs = transitions_cost + night_transitions_cost + night_shift_distribution_cost + ten_days_a_row_cost
            ten_days_a_row_str = ""
            for j in range(len(ten_days_a_row)):
                ten_days_a_row_str += f"{ten_days_a_row[j]} "

            table.add_row([team, employee,
                           transitions, transitions_cost,
                           night_transitions, night_transitions_cost,
                           night_shift_distribution, night_shift_distribution_cost,
                           shift_distribution, shift_distribution_cost,
                           ten_days_a_row_str, ten_days_a_row_cost, sum_costs],
                          divider=len(self.transition_cost) == i + 1 or team != next_team)
        table.add_row(["sum_costs", "", str(transitions_sum), str(transitions_cost_sum),
                       str(night_transition_sum), str(night_transitions_cost_sum),
                       str(night_shift_distribution_sum), str(night_shift_distribution_cost_sum),
                       str(shift_distribution_sum), str(shift_distribution_cost_sum),
                       str(ten_days_a_row_sum), str(ten_days_a_row_cost_sum),
                       self.ObjectiveValue()])
        print(table)
        print("transitions = Number of changes between working day and day off")
        print("transition_cost = (transitions * 3)^2")
        print("night_transitions = Number of changes between working night shift day and any other day")
        print("night_transitions_cost = (night_transitions * 7)^2")
        print("night_shift_distribution = Number of worked night shifts")
        print("night_shift_distribution_cost = (night_shift_distribution * 2)^2")
        print("five_days_a_row = Number of periods worked 6 days in a row")
        print("five_days_a_row_cost = (five_days_a_row * 10000000)^2")
        self.solution_count += 1
        #if self.solution_count >= 10:
        #    self.StopSearch()
        if self.solution_count%5 == 0:
            needed_keyss = get_keys(weeks_input, teams_input)
            time_now = f"{time.time() - self.start_time}"
            x = {var: self.Value(self.all_vars[var]) == 1 for var in self.all_vars.keys()}
            filtered_results = {key: int_var for key, int_var in x.items() if key in needed_keyss}
            write_to_excel(filtered_results, teams_input, weeks_input, ["M", "A", "N"],
                           f"hello_world_{time_now}.xlsx")
            output = []
            output.append("--------------------")
            output.append("gearbeitete Schichten")
            for key, value in self.shift_distribution.items():
                output.append(f"{int(self.Value(value) / 3)}")
                output.append("")
            output.append("--------------------")
            output.append("durchshnittliche Schichten pro Woche")
            for key, value in self.shift_distribution.items():
                output.append(f"{(self.Value(value) / 3) / len(weeks_input)}")
                output.append("")
            output.append("--------------------")
            output.append("gearbeitete Nachtschichten")
            for key, value in self.night_shift_distribution.items():
                output.append(f"{int(self.Value(value) / 10)}")
                output.append("")
            output.append("--------------------")
            output.append("Überstunden")
            for key, value in self.ten_days_a_row.items():
                output.append(f"{int(sum([self.Value(x) / 10000 for x in value]))}")
                output.append("")
            output.append("--------------------")
            output.append("genommene Urlaubstage")
            for team in teams_input:
                for employee in team.employees:
                    ueberstunden = 0
                    for week in weeks_input:
                        for day in week.days:
                            if self.Value(self.all_vars[f"{week}_{day}_vac_{team}_{employee}_vac"]) == 1:
                                ueberstunden += 1
                    output.append(str(ueberstunden))
                    output.append("")
            output.append("--------------------")
            output.append("Krankheitstage")
            for team in teams_input:
                for employee in team.employees:
                    krankheit = 0
                    for week in weeks_input:
                        for day in week.days:
                            if self.Value(self.all_vars[f"{week}_{day}_ill_{team}_{employee}_ill"]) == 1:
                                krankheit += 1
                    output.append(str(krankheit))
                    output.append("")
            output.append("--------------------")
            with open(f'output_{time_now}.txt', 'w') as f:
                for string in output:
                    f.write(string + '\n')

            values_till_now = [str(transitions_sum), str(transitions_cost_sum),
                               str(night_transition_sum), str(night_transitions_cost_sum),
                               str(night_shift_distribution_sum), str(night_shift_distribution_cost_sum),
                               str(shift_distribution_sum), str(shift_distribution_cost_sum),
                               str(ten_days_a_row_sum), str(ten_days_a_row_cost_sum),
                               self.ObjectiveValue()]
            with open(f'values_{time_now}.txt', 'w') as f:
                for string in values_till_now:
                    f.write(str(string) + '\n')


class MyAnalysisSolutionPrinter(CpSolverSolutionCallback):
    def __init__(self, data, all_vars):
        CpSolverSolutionCallback.__init__(self)
        self.solution_count = 0
        self.start_time = time.time()
        self.data = data
        self.all_vars = all_vars

    def on_solution_callback(self) -> None:
        print(
            f"Solution {self.solution_count}, time {time.time() - self.start_time}s, objective {self.ObjectiveValue()}")
        self.solution_count += 1
        for empl, skills in self.data.items():
            print(f"{empl} : {[skill for skill, value in skills.items() if self.Value(value) == 1]}")
        time_now = f"{time.time() - self.start_time}"
        values_till_now = [f"{empl} : {[skill for skill, value in skills.items() if self.Value(value) == 1]}" for
                           empl, skills in self.data.items()]
        with open(f'output_{time_now}.txt', 'w') as f:
            for string in values_till_now:
                f.write(str(string) + '\n')
        with open(f'values_{time_now}.txt', 'w') as f:
            f.write(str(self.ObjectiveValue()))
        needed_keyss = get_keys(weeks_input, teams_input)
        x = {var: self.Value(self.all_vars[var]) == 1 for var in self.all_vars.keys()}
        filtered_results = {key: int_var for key, int_var in x.items() if key in needed_keyss}
        write_to_excel(filtered_results, teams_input, weeks_input, ["M", "A", "N"],
                       f"hello_world_{time_now}.xlsx")

def get_model(model: cp_model.CpModel, all_vars: dict[str, cp_model.IntVar], transitions: dict[str, cp_model.IntVar],
              night_transitions: dict[str, cp_model.IntVar], night_shift_distribution: dict[str, cp_model.IntVar], shift_distribution: dict[str, cp_model.IntVar], ten_days_a_row_cost: dict[str, list[cp_model.IntVar]], teams:list[Team], weeks: list[Week]) -> \
        dict[str, bool] | None:
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 8
    solver.parameters.max_time_in_seconds = 240000.0
    solution_printer = MySolutionPrinter(transitions, night_transitions, night_shift_distribution, shift_distribution, ten_days_a_row_cost, all_vars)
    status = solver.Solve(model, solution_printer)
    print("TIME LIMIT REACHED")
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        if status == cp_model.OPTIMAL:
            print("OPTIMAL")
        if status == cp_model.FEASIBLE:
            print("FEASIBLE")
        print("--------------------")
        print("gearbeitete Schichten")
        for key, value in shift_distribution.items():
            print(f"{int(solver.Value(value)/3)}")
            print()
        print("--------------------")
        print("durchshnittliche Schichten pro Woche")
        for key, value in shift_distribution.items():
            print(f"{(solver.Value(value)/3)/len(weeks)}")
            print()
        print("--------------------")
        print("gearbeitete Nachtschichten")
        for key, value in night_shift_distribution.items():
            print(f"{int(solver.Value(value) / 10)}")
            print()
        print("--------------------")
        print("Überstunden")
        for key, value in ten_days_a_row_cost.items():
            print(f"{int(sum([solver.Value(x)/10000 for x in value]))}")
            print()
        print("--------------------")
        print("genommene Urlaubstage")
        for team in teams:
            for employee in team.employees:
                ueberstunden = 0
                for week in weeks:
                    for day in week.days:
                        if solver.Value(all_vars[f"{week}_{day}_vac_{team}_{employee}_vac"]) == 1:
                            ueberstunden += 1
                print(str(ueberstunden))
                print()
        print("--------------------")
        print("Krankheitstage")
        for team in teams:
            for employee in team.employees:
                krankheit = 0
                for week in weeks:
                    for day in week.days:
                        if solver.Value(all_vars[f"{week}_{day}_ill_{team}_{employee}_ill"]) == 1:
                            krankheit += 1
                print(str(krankheit))
                print()
        print("--------------------")
        return {var: solver.Value(all_vars[var]) == 1 for var in all_vars.keys()}
    else:
        if status == cp_model.INFEASIBLE:
            print("INFEASIBLE")
        if status == cp_model.UNKNOWN:
            print("UNKNOWN")
        if status == cp_model.MODEL_INVALID:
            print("MODEL_INVALID")
        return None


def main(weeks: list[Week], weeks_plus_one: list[Week], teams: list[Team], true_keys: list[str]) -> dict[str, bool] | None:
    model = cp_model.CpModel()

    # create all vars
    all_vars: dict[str, cp_model.IntVar] = {}
    for key in get_keys(weeks_plus_one, teams):
        all_vars[key] = model.NewBoolVar(key)

    for key in true_keys:
        model.Add(all_vars[key] == 1)

    # Hard constraints
    add_every_shift_skill_is_assigned(model, weeks_plus_one, teams, all_vars)
    add_one_employee_only_one_shift_per_day(model, weeks_plus_one, teams, all_vars)
    add_employee_cant_do_what_he_cant(model, weeks_plus_one, teams, all_vars)
    add_employees_can_only_work_with_team_members(model, weeks_plus_one, teams, all_vars)
    add_one_employee_only_works_five_days_a_week(model, weeks_plus_one, teams, all_vars)
    add_one_employee_works_the_same_shift_a_week(model, weeks_plus_one, teams, all_vars)
    add_every_employee_have_two_shift_pause(model, weeks_plus_one, teams, all_vars)
    add_shift_cycle(model, weeks_plus_one, teams, all_vars, ["M", "A", "N"])
    add_at_least_one_shift_manager_per_team_per_day(model, weeks_plus_one, teams, all_vars)
    add_one_employee_only_works_five_days_in_a_row(model, weeks_plus_one, teams, all_vars)
    #add_one_employee_works_max_ten_days_in_a_row(model, weeks_plus_one, teams, all_vars)
    # add_illness_manually(model, weeks, all_vars, "Team1_P5", [f"Week1_{day.name}" for day in weeks[0].days])
    #add_absence_manually(model, weeks, all_vars, "Team1_P6", [f"Week1_{day.name}" for day in weeks[0].days])
    #add_absence_manually(model, weeks, all_vars, "Team1_P6", [f"Week2_{day.name}" for day in weeks[0].days[:3]])
    add_vacations(model, weeks, teams, all_vars, 5, 7)
    add_illness(model, weeks, teams, all_vars, 5, 5)
    add_vac_not_in_ill(model, weeks, teams, all_vars)
    add_employee_works_night_shifts_in_a_row(model, weeks, teams, all_vars, "N")

    # Soft constrains
    minimize_var_work_in_row, transition_cost_per_employee = \
        add_employee_should_work_in_a_row(model, weeks, teams, all_vars, 3)
    minimize_var_work_in_row_at_night, night_transition_cost_per_employee = \
        add_employee_should_work_night_shifts_in_a_row(model, weeks, teams, all_vars, 7 * 4 * 2, "N")
    minimize_var_same_night_shift_amount_per_employee, night_shift_cost_per_employee = \
        add_every_employee_should_do_same_amount_night_shifts(model, weeks, teams, all_vars, 10, "N")
    minimize_var_same_shift_amount_per_employee, shift_cost_per_employee = add_every_employee_should_do_same_amount_of_shifts(model, weeks, teams, all_vars, 10)
    # add_an_employee_should_do_the_same_job_a_week(model, weeks, teams, all_vars)
    # minimize_five_days_a_row, five_days_a_row_cost_per_employee = add_one_employee_should_work_max_five_days_in_a_row(model, weeks, teams, all_vars, 10000)
    minimize_ten_days_a_row, ten_days_a_row_cost_per_employee = add_one_employee_should_work_max_ten_days_in_a_row(model, weeks, teams, all_vars, 10000)

    skills_employee, minimize_skills_cost = add_minimize_needed_skills(model, weeks, teams, all_vars, 0)
    minimize_needed_empl = add_minimize_needed_employees(model, weeks, teams, all_vars, 100)
    model.Minimize(minimize_needed_empl + minimize_skills_cost)

    print("All Rules added. Start Solver")
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 8
    solver.parameters.max_time_in_seconds = 1200.0
    status = solver.Solve(model, MyAnalysisSolutionPrinter(skills_employee, all_vars))
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        if status == cp_model.OPTIMAL:
            print("OPTIMAL")
        if status == cp_model.FEASIBLE:
            print("FEASIBLE")
        for empl, skills in skills_employee.items():
            print(f"{empl} : {[skill for skill, value in skills.items() if solver.Value(value) == 1]}")
        return {var: solver.Value(all_vars[var]) == 1 for var in all_vars.keys()}
    else:
        if status == cp_model.INFEASIBLE:
            print("INFEASIBLE")
        if status == cp_model.UNKNOWN:
            print("UNKNOWN")
        if status == cp_model.MODEL_INVALID:
            print("MODEL_INVALID")
        return None
    #model.Minimize(
    #    minimize_var_work_in_row +
    #    minimize_var_work_in_row_at_night +
    #    minimize_var_same_night_shift_amount_per_employee +
    #    minimize_var_same_shift_amount_per_employee +
    #    minimize_ten_days_a_row)
    print("All Rules added. Start Solver")
    model_result = get_model(model, all_vars, transition_cost_per_employee, night_transition_cost_per_employee,
                             night_shift_cost_per_employee, shift_cost_per_employee, ten_days_a_row_cost_per_employee, teams, weeks)
    return model_result


def get_keys(weeks: list[Week], teams: list[Team]) -> list[str]:
    keys: list[str] = []
    for team in teams:
        for employee in team.employees:
            for week in weeks:
                for day in week.days:
                    for shift in day.shifts:
                        for needed_skill in shift.needed_skills:
                            keys.append(f"{week}_{day}_{shift}_{team}_{employee}_{needed_skill}")
                    keys.append(f"{week}_{day}_vac_{team}_{employee}_vac")
                    keys.append(f"{week}_{day}_ill_{team}_{employee}_ill")

    return keys


if __name__ == "__main__":
    filename = None  # 'hello_world.xlsx'
    if filename is not None:
        keys = read_from_excel(filename)
        highest_week_number = max([int(k.split('_')[0][4:]) for k in keys])
    else:
        keys = []
        highest_week_number = 0
    teams_input = get_teams_input_data()
    weeks_input_plus_one = get_weeks_input_data(highest_week_number * 7 + 4 * 7 +1)
    weeks_input = get_weeks_input_data(highest_week_number * 7 + 4 * 7)
    result = main(weeks=weeks_input, weeks_plus_one=weeks_input_plus_one, teams=teams_input, true_keys=keys)
    needed_keys = get_keys(weeks_input, teams_input)
    filtered_result = {key: int_var for key, int_var in result.items() if key in needed_keys}

    if result is not None:
        write_to_excel(filtered_result, teams_input, weeks_input, ["M", "A", "N"],
                       filename if filename else "hello_world.xlsx")
