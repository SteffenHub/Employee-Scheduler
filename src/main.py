import time
from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import CpSolverSolutionCallback
from prettytable import PrettyTable

from src.excel_interface import write_to_excel, read_from_excel
from src.model.ConsoleOutput import ConsoleOutput
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

from src.model.Input_data_creator import get_teams_input_data, get_weeks_input_data
from src.model.Team import Team
from src.model.Week import Week


class CustomSolutionPrinter(CpSolverSolutionCallback):

    def __init__(self, output: list[ConsoleOutput], all_vars: dict[str, cp_model.IntVar]):
        CpSolverSolutionCallback.__init__(self)
        self.output = output
        self.solution_count = 0
        self.start_time = time.time()
        self.all_vars = all_vars

    def on_solution_callback(self) -> None:
        table = PrettyTable()
        self.solution_count += 1
        print(f"Solution {self.solution_count}, time {time.time() - self.start_time}s")

        # create and set column names
        fiel_names: list[str] = ["Team", "Employee"]
        for output_item in self.output:
            fiel_names.append(output_item.column_name)
            fiel_names.append(f"{output_item.column_name} cost")
        fiel_names.append("sum_costs")
        table.field_names = fiel_names

        # sum of all employees for each column(numbers in last row)
        sums_initial_columns: list[int] = [0 for _ in self.output]
        sums_cost_columns: list[int] = [0 for _ in self.output]

        for i, teamEmployee in enumerate(self.output[0].data.keys()):
            team, employee = teamEmployee.split(":")
            next_team = list(self.output[0].data.keys())[i + 1].split(":")[0] if i < len(
                self.output[0].data) - 1 else team
            is_last_empl_in_team: bool = len(self.output[0].data) == i + 1 or team != next_team

            # create one row, representing one employee
            row_data = [team, employee]
            all_cost_sum: int = 0
            for j, output_item in enumerate(self.output):
                value = self.Value(output_item.data[teamEmployee])
                initial = int(value / output_item.cost)
                objective_cost = value ** 2

                row_data.append(initial)
                sums_initial_columns[j] += initial

                row_data.append(objective_cost)
                all_cost_sum += objective_cost
                sums_cost_columns[j] += objective_cost

            row_data.append(all_cost_sum)
            table.add_row(row_data, divider=is_last_empl_in_team)

        # create and add last row containing the sum of all values above it
        last_row = ["sum costs", ""]
        for i in range(len(sums_initial_columns)):
            last_row.append(sums_initial_columns[i])
            last_row.append(sums_cost_columns[i])
        last_row.append(int(self.ObjectiveValue()))
        table.add_row(last_row)
        print(table)

        # write result to excel
        needed_keys = get_keys(weeks_input, teams_input)
        time_now = f"{time.time() - self.start_time}"
        solution = {var: self.Value(self.all_vars[var]) == 1 for var in self.all_vars.keys()}
        filtered_solution = {key: int_var for key, int_var in solution.items() if key in needed_keys}
        write_to_excel(filtered_solution, teams_input, weeks_input, ["M", "A", "N"],
                       f"scheduler_result_{time_now}.xlsx")


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


def get_model(model: cp_model.CpModel, all_vars: dict[str, cp_model.IntVar], console_output: list[ConsoleOutput],
              teams: list[Team], weeks: list[Week]) -> dict[str, bool] | None:
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 7
    solver.parameters.max_time_in_seconds = 1200.0
    status = solver.Solve(model, CustomSolutionPrinter(console_output, all_vars))
    print("TIME LIMIT REACHED")
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        if status == cp_model.OPTIMAL:
            print("OPTIMAL")
        if status == cp_model.FEASIBLE:
            print("FEASIBLE")
        return {var: solver.Value(all_vars[var]) == 1 for var in all_vars.keys()}
    else:
        if status == cp_model.INFEASIBLE:
            print("INFEASIBLE")
        if status == cp_model.UNKNOWN:
            print("UNKNOWN")
        if status == cp_model.MODEL_INVALID:
            print("MODEL_INVALID")
        return None


def main(weeks: list[Week], weeks_plus_one: list[Week], teams: list[Team], true_keys: list[str]) -> dict[
                                                                                                        str, bool] | None:
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
    # add_one_employee_only_works_five_days_in_a_row(model, weeks_plus_one, teams, all_vars)
    # add_one_employee_works_max_ten_days_in_a_row(model, weeks_plus_one, teams, all_vars)
    # add_illness_manually(model, weeks, all_vars, "Team1_P5", [f"Week1_{day.name}" for day in weeks[0].days])
    # add_absence_manually(model, weeks, all_vars, "Team1_P6", [f"Week1_{day.name}" for day in weeks[0].days])
    # add_absence_manually(model, weeks, all_vars, "Team1_P6", [f"Week2_{day.name}" for day in weeks[0].days[:3]])
    # add_vacations(model, weeks, teams, all_vars, 5, 7)
    # add_illness(model, weeks, teams, all_vars, 5, 5)
    # add_vac_not_in_ill(model, weeks, teams, all_vars)
    # add_employee_works_night_shifts_in_a_row(model, weeks, teams, all_vars, "N")

    # Soft constrains
    minimize_var_work_in_row, transition_cost_per_employee = \
        add_employee_should_work_in_a_row(model, weeks, teams, all_vars, 3)
    minimize_var_work_in_row_at_night, night_transition_cost_per_employee = \
        add_employee_should_work_night_shifts_in_a_row(model, weeks, teams, all_vars, 7 * 4 * 2, "N")
    minimize_var_same_night_shift_amount_per_employee, night_shift_cost_per_employee = \
        add_every_employee_should_do_same_amount_night_shifts(model, weeks, teams, all_vars, 10, "N")
    minimize_var_same_shift_amount_per_employee, shift_cost_per_employee = add_every_employee_should_do_same_amount_of_shifts(
        model, weeks, teams, all_vars, 10)
    # add_an_employee_should_do_the_same_job_a_week(model, weeks, teams, all_vars)
    minimize_five_days_a_row, five_days_a_row_cost_per_employee = add_one_employee_should_work_max_five_days_in_a_row(
        model, weeks, teams, all_vars, 10000)
    # minimize_ten_days_a_row, ten_days_a_row_cost_per_employee = add_one_employee_should_work_max_ten_days_in_a_row(model, weeks, teams, all_vars, 10000)
    # skills_employee, minimize_skills_cost = add_minimize_needed_skills(model, weeks, teams, all_vars, 1)
    # minimize_needed_empl = add_minimize_needed_employees(model, weeks, teams, all_vars, 100)
    # model.Minimize(minimize_needed_empl + minimize_skills_cost)

    model.Minimize(minimize_var_work_in_row +
                   minimize_var_work_in_row_at_night +
                   minimize_var_same_night_shift_amount_per_employee +
                   minimize_var_same_shift_amount_per_employee +
                   minimize_five_days_a_row)

    print("All Rules added. Start Solver")
    model_result = get_model(model, all_vars,
                             [ConsoleOutput(column_name="transition", data=transition_cost_per_employee, cost=3),
                              ConsoleOutput(column_name="night transition", data=night_transition_cost_per_employee,
                                            cost=56),
                              ConsoleOutput(column_name="night shift distribution", data=night_shift_cost_per_employee,
                                            cost=10),
                              ConsoleOutput(column_name="shift distribution", data=shift_cost_per_employee, cost=10),
                              ConsoleOutput(column_name="overtime", data=five_days_a_row_cost_per_employee,
                                            cost=10000)],
                             teams, weeks)
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
    weeks_input_plus_one = get_weeks_input_data(highest_week_number * 7 + 4 * 7 + 1)
    weeks_input = get_weeks_input_data(highest_week_number * 7 + 4 * 7)
    result = main(weeks=weeks_input, weeks_plus_one=weeks_input_plus_one, teams=teams_input, true_keys=keys)
    needed_keys = get_keys(weeks_input, teams_input)
    filtered_result = {key: int_var for key, int_var in result.items() if key in needed_keys}

    if result is not None:
        write_to_excel(filtered_result, teams_input, weeks_input, ["M", "A", "N"],
                       filename if filename else "scheduler_result_final.xlsx")
