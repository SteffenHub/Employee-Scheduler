import unittest

from ortools.sat.python import cp_model

from src.model.Day import Day
from src.model.Employee import Employee
from src.model.Shift import Shift
from src.model.Skill import Skill
from src.model.Team import Team
from src.model.Week import Week
from src.rule_builder import add_one_employee_only_works_five_days_a_week


class TestAddOneEmployeeOnlyWorksFiveDaysAWeek(unittest.TestCase):

    def setUp(self):
        # Setup cp_model, weeks, teams, and all_vars for testing
        self.model = cp_model.CpModel()
        self.all_skills = [Skill('skill1')]
        self.weeks = [
            Week(days=[
                Day(shifts=[
                    Shift(needed_skills=self.all_skills,name="shift1"),
                ], name="day1"),
                Day(shifts=[
                    Shift(needed_skills=self.all_skills, name="shift1"),
                ], name="day2"),
                Day(shifts=[
                    Shift(needed_skills=self.all_skills, name="shift1"),
                ], name="day3"),
                Day(shifts=[
                    Shift(needed_skills=self.all_skills, name="shift1"),
                ], name="day4"),
                Day(shifts=[
                    Shift(needed_skills=self.all_skills, name="shift1"),
                ], name="day5"),
                Day(shifts=[
                    Shift(needed_skills=self.all_skills, name="shift1"),
                ], name="day6"),
                Day(shifts=[
                    Shift(needed_skills=self.all_skills, name="shift1"),
                ], name="day7")
            ], name="week1")
        ]

        self.teams = [
            Team(employees=[
                Employee(name='employee1', skills=[self.all_skills[0]])
            ], name="team1")
        ]

        self.all_vars = {
            'week1_day1_shift1_team1_employee1_skill1': self.model.NewBoolVar('e1_d1'),
            'week1_day2_shift1_team1_employee1_skill1': self.model.NewBoolVar('e1_d2'),
            'week1_day3_shift1_team1_employee1_skill1': self.model.NewBoolVar('e1_d3'),
            'week1_day4_shift1_team1_employee1_skill1': self.model.NewBoolVar('e1_d4'),
            'week1_day5_shift1_team1_employee1_skill1': self.model.NewBoolVar('e1_d5'),
            'week1_day6_shift1_team1_employee1_skill1': self.model.NewBoolVar('e1_d6'),
            'week1_day7_shift1_team1_employee1_skill1': self.model.NewBoolVar('e1_d7'),
        }

    def test_0_assignments(self):
        add_one_employee_only_works_five_days_a_week(self.model, self.weeks, self.teams, self.all_vars)
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)
        self.assertIn(status, [cp_model.FEASIBLE, cp_model.OPTIMAL])

    def test_1_assignment(self):
        add_one_employee_only_works_five_days_a_week(self.model, self.weeks, self.teams, self.all_vars)
        self.model.Add(self.all_vars['week1_day1_shift1_team1_employee1_skill1'] == 1)
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)
        self.assertIn(status, [cp_model.FEASIBLE, cp_model.OPTIMAL])

    def test_2_assignments(self):
        add_one_employee_only_works_five_days_a_week(self.model, self.weeks, self.teams, self.all_vars)
        self.model.Add(self.all_vars['week1_day1_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day7_shift1_team1_employee1_skill1'] == 1)
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)
        self.assertIn(status, [cp_model.FEASIBLE, cp_model.OPTIMAL])

    def test_3_assignments(self):
        add_one_employee_only_works_five_days_a_week(self.model, self.weeks, self.teams, self.all_vars)
        self.model.Add(self.all_vars['week1_day1_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day3_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day7_shift1_team1_employee1_skill1'] == 1)
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)
        self.assertIn(status, [cp_model.FEASIBLE, cp_model.OPTIMAL])

    def test_4_assignments(self):
        add_one_employee_only_works_five_days_a_week(self.model, self.weeks, self.teams, self.all_vars)
        self.model.Add(self.all_vars['week1_day1_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day2_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day4_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day6_shift1_team1_employee1_skill1'] == 1)
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)
        self.assertIn(status, [cp_model.FEASIBLE, cp_model.OPTIMAL])

    def test_5_assignments(self):
        add_one_employee_only_works_five_days_a_week(self.model, self.weeks, self.teams, self.all_vars)
        self.model.Add(self.all_vars['week1_day1_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day3_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day5_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day6_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day7_shift1_team1_employee1_skill1'] == 1)
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)
        self.assertIn(status, [cp_model.FEASIBLE, cp_model.OPTIMAL])

    def test_6_assignments(self):
        add_one_employee_only_works_five_days_a_week(self.model, self.weeks, self.teams, self.all_vars)
        self.model.Add(self.all_vars['week1_day2_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day3_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day4_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day5_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day6_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day7_shift1_team1_employee1_skill1'] == 1)
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)
        self.assertEqual(status, cp_model.INFEASIBLE)

    def test_7_assignments(self):
        add_one_employee_only_works_five_days_a_week(self.model, self.weeks, self.teams, self.all_vars)
        self.model.Add(self.all_vars['week1_day1_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day2_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day3_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day4_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day5_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day6_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day7_shift1_team1_employee1_skill1'] == 1)
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)
        self.assertEqual(status, cp_model.INFEASIBLE)


if __name__ == '__main__':
    unittest.main()