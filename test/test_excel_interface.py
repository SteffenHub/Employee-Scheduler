import os
from unittest import TestCase

from src.excel_interface import write_to_excel, read_from_excel
from src.model.Input_data_creator import get_teams_input_data, get_weeks_input_data


class TestReadFromExcel(TestCase):

    def test_read_from_excel(self):
        name_of_excel_file = "tmp_test_result.xlsx"

        teams = get_teams_input_data()
        weeks = get_weeks_input_data(2 * 7)

        model_result = {
            "Week1_Fr_N_Team1_P1_H:M3": True,
            "Week1_Sa_N_Team1_P1_H:M2": True,
            "Week1_Su_N_Team1_P1_H:M3": True,
            "Week2_Mo_N_Team1_P1_H:M2": True,
            "Week2_Tu_N_Team1_P1_H:M3": True,
            "Week2_We_N_Team1_P1_H:M3": True,
            "Week2_Th_N_Team1_P1_MO:M3": True,
            "Week2_Fr_N_Team1_P1_H:M3": True,
            "Week2_Sa_N_Team1_P1_H:M3": True,
            "Week2_Su_N_Team1_P1_H:M3": True,
            "Week2_Fr_N_Team1_P3_H:M3": True,
            "Week2_Sa_N_Team1_P3_H:M3": True,
            "Week2_Su_N_Team1_P3_H:M3": True,
            "Week1_Mo_A_Team1_P4_H:M3": True,
            "Week1_We_N_Team1_P4_H:M3": True,
            "Week1_Th_A_Team1_P4_H:M3": True,
            "Week1_Fr_N_Team1_P4_H:M3": True,
            "Week1_Sa_N_Team1_P4_H:M3": True,
            "Week1_Su_N_Team1_P4_H:M3": True,
            "Week2_Mo_N_Team1_P4_H:M3": True,
            "Week2_Tu_N_Team1_P4_H:M3": True,
            "Week2_We_N_Team1_P4_H:M3": True,
            "Week2_Th_N_Team1_P4_H:M3": True,
            "Week2_Fr_M_Team1_P4_H:M3": True,
            "Week1_Fr_N_Team2_P17_H:M2": True,
            "Week1_Sa_N_Team2_P17_H:M2": True,
            "Week1_Su_N_Team2_P17_H:M3": True,
            "Week2_Mo_N_Team2_P17_H:M3": True,
            "Week2_Tu_N_Team2_P17_H:M3": True,
            "Week2_We_N_Team2_P17_H:M2": True,
            "Week2_Th_N_Team2_P17_H:M3": True,
            "Week2_Fr_N_Team2_P17_H:M2": True,
            "Week2_Sa_A_Team2_P17_H:M3": True,
            "Week2_Su_N_Team2_P17_MO:M3": True,
            "Week1_Mo_N_Team2_P18_H:M2": True,
            "Week1_Tu_N_Team2_P18_H:M3": True,
            "Week1_We_N_Team2_P18_H:M3": True,
            "Week1_Th_N_Team2_P18_H:M3": True,
            "Week1_Tu_A_Team3_P27_H:M3": True,
            "Week1_We_N_Team3_P27_H:M3": True,
            "Week1_Th_N_Team3_P27_H:M2": True,
            "Week1_Fr_N_Team3_P27_H:M3": True,
            "Week1_Sa_N_Team3_P27_H:M2": True,
            "Week1_Su_N_Team3_P27_H:M3": True,
            "Week2_Mo_N_Team3_P27_H:M2": True,
            "Week2_Tu_N_Team3_P27_H:M2": True,
            "Week2_We_N_Team3_P27_H2:M1": True,
            "Week2_Th_N_Team3_P27_H1:M1": True,
            "Week2_Fr_N_Team3_P27_H:M3": True,
            "Week2_Th_N_Team3_P32_H:M2": True,
            "Week2_Fr_A_Team3_P32_H:M2": True,
            "Week2_Sa_N_Team3_P32_H:M3": True,
            "Week2_Su_N_Team3_P32_H2:M1": True,
            "Week1_Mo_N_Team3_P33_H:M3": True,
            "Week1_Tu_N_Team3_P33_H:M2": True,
            "Week1_We_N_Team3_P33_H:M2": True,
            "Week1_Th_N_Team3_P33_H:M3": True,
            "Week1_Fr_N_Team3_P33_H:M3": True,
            "Week1_Sa_N_Team3_P33_H:M3": True,
            "Week1_Su_N_Team3_P33_H:M3": True,
            "Week1_We_N_Team3_P34_H:M3": True,
            "Week1_Th_N_Team3_P34_H:M2": True,
            "Week1_Fr_N_Team3_P34_H2:M1": True,
            "Week1_Sa_N_Team3_P34_H1:M1": True,
            "Week1_Su_N_Team3_P34_H:M2": True,
            "Week2_Mo_N_Team3_P34_H:M2": True,
            "Week2_Tu_N_Team3_P34_H2:M1": True,
            "Week2_We_N_Team3_P34_H:M3": True,
            "Week2_Th_N_Team3_P34_H:M3": True,
        }

        write_to_excel(model_result, teams, weeks, ["M", "A", "N"], name_of_excel_file=name_of_excel_file, save_in_directory="../test")

        actual = read_from_excel("../test/" + name_of_excel_file)
        if os.path.isfile(name_of_excel_file):
            os.remove(name_of_excel_file)
        else:
            print(f"test file cant be removed: ../test/{name_of_excel_file}")

        expected = [key for key in model_result.keys() if model_result[key] is True]

        for key in expected:
            self.assertTrue(key in actual, f"Key {key} not found in actual result")
