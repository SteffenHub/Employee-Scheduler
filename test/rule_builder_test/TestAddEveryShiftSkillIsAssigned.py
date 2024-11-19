import unittest

from ortools.sat.python import cp_model

from src.model.Day import Day
from src.model.Employee import Employee
from src.model.Shift import Shift
from src.model.Skill import Skill
from src.model.Team import Team
from src.model.Week import Week
from src.rule_builder import add_every_shift_skill_is_assigned


class TestAddEveryShiftSkillIsAssigned(unittest.TestCase):

    def setUp(self):
        # Setup cp_model, weeks, teams, and all_vars for testing
        self.model = cp_model.CpModel()
        self.all_skills = [Skill('skill1'), Skill('skill2')]
        self.weeks = [
            Week(days=[
                Day(shifts=[
                    Shift(needed_skills=self.all_skills,name="shift1"),
                    Shift(needed_skills=self.all_skills, name="shift2")
                ], name="day1")
            ], name="week1")
        ]

        self.teams = [
            Team(employees=[
                Employee(name='employee1', skills=self.all_skills), Employee(name='employee2',skills=self.all_skills)
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

    def test_add_every_shift_skill_is_assigned(self):
        # Call the function to add constraints
        add_every_shift_skill_is_assigned(self.model, self.weeks, self.teams, self.all_vars)

        # Define a solver and solve the model to check constraints
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)

        # Check if the solution is feasible
        self.assertIn(status, [cp_model.FEASIBLE, cp_model.OPTIMAL])

        # Verify if each skill is assigned exactly to one employee
        for week in self.weeks:
            for day in week.days:
                for shift in day.shifts:
                    for skill in shift.needed_skills:
                        assigned = sum(1 for team in self.teams for employee in team.employees
                                       if solver.BooleanValue(
                            self.all_vars[f"{week}_{day}_{shift}_{team}_{employee}_{skill}"]))
                        self.assertEqual(assigned, 1, f"Skill {skill} not assigned exactly to one employee.")


if __name__ == '__main__':
    unittest.main()
