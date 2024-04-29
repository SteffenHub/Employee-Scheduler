from unittest import TestCase

from ortools.sat.python import cp_model

from src.main import get_keys
from src.model.Input_data_creator import get_teams_input_data, get_weeks_input_data
from src.rule_builder import add_every_shift_skill_is_assigned, add_one_employee_only_one_shift_per_day, \
    add_every_employee_should_do_same_amount_of_shifts


class TestRuleBuilder(TestCase):

    def setUp(self):
        self.weeks = get_weeks_input_data(9)
        self.teams = get_teams_input_data()
        self.model = cp_model.CpModel()
        self.all_vars = {}
        for key in get_keys(self.weeks, self.teams):
            self.all_vars[key] = self.model.NewBoolVar(key)

    def solve(self, model, all_vars) -> dict[str, bool] | None:
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            result = {}
            for var in all_vars.keys():
                result[var] = solver.Value(all_vars[var]) == 1
            return result
        else:
            return None

    def solve_with_objective_value(self, model, all_vars) -> tuple[dict[str, bool], float] | None:
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            result = {}
            for var in all_vars.keys():
                result[var] = solver.Value(all_vars[var]) == 1
            return result, solver.objective_value
        else:
            return None

    def test_only_one_shift_per_employee_per_day(self):
        add_every_shift_skill_is_assigned(self.model, self.weeks, self.teams, self.all_vars)
        add_one_employee_only_one_shift_per_day(self.model, self.weeks, self.teams, self.all_vars)
        result_keys: dict[str, bool] | None = self.solve(self.model, self.all_vars)
        if result_keys is None:
            self.fail()
        for team in self.teams:
            for employee in team.employees:
                for week in self.weeks:
                    for day in week.days:
                        summe = 0
                        for shift in day.shifts:
                            for skill in shift.needed_skills:
                                if result_keys[f"{week}_{day}_{shift}_{team}_{employee}_{skill}"]:
                                    summe += 1
                        self.assertTrue(summe <= 1)

    def test_not_one_shift_per_employee_per_day(self):
        self.teams = [self.teams[0]]
        add_every_shift_skill_is_assigned(self.model, self.weeks, self.teams, self.all_vars)
        add_one_employee_only_one_shift_per_day(self.model, self.weeks, self.teams, self.all_vars)
        result_keys: dict[str, bool] | None = self.solve(self.model, self.all_vars)
        self.assertIsNone(result_keys)

    def test_add_every_shift_skill_is_assigned(self):
        def run():
            for week in self.weeks:
                for day in week.days:
                    for shift in day.shifts:
                        for skill in shift.needed_skills:
                            summe = 0
                            for team in self.teams:
                                for employee in team.employees:
                                    if result_keys[f"{week}_{day}_{shift}_{team}_{employee}_{skill}"]:
                                        summe += 1
                            self.assertEqual(summe, 1)

        add_every_shift_skill_is_assigned(self.model, self.weeks, self.teams, self.all_vars)
        result_keys: dict[str, bool] | None = self.solve(self.model, self.all_vars)
        if result_keys is None:
            self.fail()
        run()

    def test_add_every_shift_skill_is_not_assigned(self):
        week = self.weeks[0]
        day = week.days[0]
        shift = day.shifts[0]
        skill = shift.needed_skills[0]
        for team in self.teams:
            for employee in team.employees:
                self.model.Add(self.all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{skill}"] == 0)
        add_every_shift_skill_is_assigned(self.model, self.weeks, self.teams, self.all_vars)
        result_keys: dict[str, bool] | None = self.solve(self.model, self.all_vars)
        self.assertIsNone(result_keys)

    def test_soft_same_amount_shifts(self):
        def get_value():
            value = 0
            for team in self.teams:
                for employee in team.employees:
                    value_emp = 0
                    for week in self.weeks:
                        for day in week.days:
                            for shift in day.shifts:
                                for skill in shift.needed_skills:
                                    if result_keys[f"{week}_{day}_{shift}_{team}_{employee}_{skill}"]:
                                        value_emp += 1
                    value += (value_emp * 3) ** 2
            return value

        add_every_shift_skill_is_assigned(self.model, self.weeks, self.teams, self.all_vars)
        add_one_employee_only_one_shift_per_day(self.model, self.weeks, self.teams, self.all_vars)
        value, another = add_every_employee_should_do_same_amount_of_shifts(self.model, self.weeks, self.teams, self.all_vars, 3)
        self.model.Minimize(value)
        result_keys, value = self.solve_with_objective_value(self.model, self.all_vars)
        if result_keys is None:
            self.fail()
        self.assertEqual(value, get_value())
