import unittest

from ortools.sat.python import cp_model

from src.model.Day import Day
from src.model.Employee import Employee
from src.model.Shift import Shift
from src.model.Skill import Skill
from src.model.Team import Team
from src.model.Week import Week
from src.rule_builder import add_one_employee_only_one_shift_per_day


class TestAddOneEmployeeOnlyOneShiftPerDay(unittest.TestCase):

    def setUp(self):
        # Setup cp_model, weeks, teams, and all_vars for testing
        self.model = cp_model.CpModel()
        self.all_skills = [Skill('skill1'), Skill('skill2')]
        self.weeks = [
            Week(days=[
                Day(shifts=[
                    Shift(needed_skills=self.all_skills, name="shift1"),
                    Shift(needed_skills=self.all_skills, name="shift2")
                ], name="day1")
            ], name="week1")
        ]

        self.teams = [
            Team(employees=[
                Employee(name='employee1', skills=self.all_skills), Employee(name='employee2', skills=self.all_skills)
            ], name="team1")
        ]

        self.all_vars = {
            'week1_day1_shift1_team1_employee1_skill1': self.model.NewBoolVar('e1_s1'),
            'week1_day1_shift1_team1_employee1_skill2': self.model.NewBoolVar('e1_s2'),
            'week1_day1_shift1_team1_employee2_skill1': self.model.NewBoolVar('e2_s1'),
            'week1_day1_shift1_team1_employee2_skill2': self.model.NewBoolVar('e2_s2'),
            'week1_day1_shift2_team1_employee1_skill1': self.model.NewBoolVar('e1_s1'),
            'week1_day1_shift2_team1_employee1_skill2': self.model.NewBoolVar('e1_s2'),
            'week1_day1_shift2_team1_employee2_skill1': self.model.NewBoolVar('e2_s1'),
            'week1_day1_shift2_team1_employee2_skill2': self.model.NewBoolVar('e2_s2'),
        }

    def test_single_employee_single_shift(self):
        # Test case for single employee with one shift per day constraint
        add_one_employee_only_one_shift_per_day(self.model, self.weeks, self.teams, self.all_vars)
        self.model.Add(self.all_vars['week1_day1_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day1_shift2_team1_employee2_skill2'] == 1)
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)
        self.assertIn(status, [cp_model.FEASIBLE, cp_model.OPTIMAL])

    def test_multiple_shifts_per_employee_per_day(self):
        # Test case for single employee with multiple shift per day constraint
        add_one_employee_only_one_shift_per_day(self.model, self.weeks, self.teams, self.all_vars)
        self.model.Add(self.all_vars['week1_day1_shift1_team1_employee1_skill1'] == 1)
        self.model.Add(self.all_vars['week1_day1_shift1_team1_employee1_skill2'] == 1)
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)
        self.assertEqual(status, cp_model.INFEASIBLE)


if __name__ == '__main__':
    unittest.main()
