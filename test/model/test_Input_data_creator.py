from unittest import TestCase

from src.model.Input_data_creator import create_input_data


class TestInputDataCreator(TestCase):
    def test_create_input_data_less_than_a_week(self):
        actual_weeks, _ = create_input_data(3)
        self.assertEqual(1, len(actual_weeks))
        self.assertEqual("Week1", actual_weeks[0].name)
        self.assertEqual(3, len(actual_weeks[0].days))
        self.assertEqual("Mo", actual_weeks[0].days[0].name)
        self.assertEqual("Tu", actual_weeks[0].days[1].name)
        self.assertEqual("We", actual_weeks[0].days[2].name)

    def test_create_input_data_more_than_a_week(self):
        actual_weeks, _ = create_input_data(7+2)
        self.assertEqual(2, len(actual_weeks))
        self.assertEqual("Week1", actual_weeks[0].name)
        self.assertEqual("Week2", actual_weeks[1].name)
        self.assertEqual(7, len(actual_weeks[0].days))
        self.assertEqual(2, len(actual_weeks[1].days))
        self.assertEqual("Mo", actual_weeks[0].days[0].name)
        self.assertEqual("Tu", actual_weeks[0].days[1].name)
        self.assertEqual("We", actual_weeks[0].days[2].name)
        self.assertEqual("Th", actual_weeks[0].days[3].name)
        self.assertEqual("Fr", actual_weeks[0].days[4].name)
        self.assertEqual("Sa", actual_weeks[0].days[5].name)
        self.assertEqual("Su", actual_weeks[0].days[6].name)
        self.assertEqual("Mo", actual_weeks[1].days[0].name)
        self.assertEqual("Tu", actual_weeks[1].days[1].name)

    def test_create_input_data_more_than_two_weeks(self):
        actual_weeks, _ = create_input_data(7+7+3)
        self.assertEqual(3, len(actual_weeks))
        self.assertEqual("Week1", actual_weeks[0].name)
        self.assertEqual("Week2", actual_weeks[1].name)
        self.assertEqual("Week3", actual_weeks[2].name)
        self.assertEqual(7, len(actual_weeks[0].days))
        self.assertEqual(7, len(actual_weeks[1].days))
        self.assertEqual(3, len(actual_weeks[2].days))
        self.assertEqual("Mo", actual_weeks[0].days[0].name)
        self.assertEqual("Tu", actual_weeks[0].days[1].name)
        self.assertEqual("We", actual_weeks[0].days[2].name)
        self.assertEqual("Th", actual_weeks[0].days[3].name)
        self.assertEqual("Fr", actual_weeks[0].days[4].name)
        self.assertEqual("Sa", actual_weeks[0].days[5].name)
        self.assertEqual("Su", actual_weeks[0].days[6].name)
        self.assertEqual("Mo", actual_weeks[1].days[0].name)
        self.assertEqual("Tu", actual_weeks[1].days[1].name)
        self.assertEqual("We", actual_weeks[1].days[2].name)
        self.assertEqual("Th", actual_weeks[1].days[3].name)
        self.assertEqual("Fr", actual_weeks[1].days[4].name)
        self.assertEqual("Sa", actual_weeks[1].days[5].name)
        self.assertEqual("Su", actual_weeks[1].days[6].name)
        self.assertEqual("Mo", actual_weeks[2].days[0].name)
        self.assertEqual("Tu", actual_weeks[2].days[1].name)
        self.assertEqual("We", actual_weeks[2].days[2].name)


