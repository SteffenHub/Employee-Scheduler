
import re
from typing import Dict, List

from openpyxl.styles import PatternFill, Side, Border
from openpyxl.workbook import Workbook

from model.Team import Team
from model.Week import Week


def write_to_excel(model_result: Dict[str, bool], teams: List[Team], weeks: List[Week]):
    workbook = Workbook()
    sheet = workbook.active

    colors = {"F": PatternFill(start_color='92d050', end_color='92d050', fill_type='solid'),
              "S": PatternFill(start_color='ffc000', end_color='ffc000', fill_type='solid'),
              "N": PatternFill(start_color='00b0f0', end_color='00b0f0', fill_type='solid'),
              "MB:T2": PatternFill(start_color='ff99ff', end_color='ff99ff', fill_type='solid'),
              "P1:T2": PatternFill(start_color='ff99ff', end_color='ff99ff', fill_type='solid'),
              "P2:T2": PatternFill(start_color='ff99ff', end_color='ff99ff', fill_type='solid'),
              "P1:T1": PatternFill(start_color='99ff99', end_color='99ff99', fill_type='solid'),
              "MB:ET": PatternFill(start_color='66ffff', end_color='66ffff', fill_type='solid'),
              "P:ET": PatternFill(start_color='66ffff', end_color='66ffff', fill_type='solid'),
              "MB:KSS": PatternFill(start_color='cc9900', end_color='cc9900', fill_type='solid'),
              "weekend": PatternFill(start_color='f3af9a', end_color='f3af9a', fill_type='solid'),
              "Team1": PatternFill(start_color='fff2cc', end_color='fff2cc', fill_type='solid'),
              "Team2": PatternFill(start_color='e2f0d9', end_color='e2f0d9', fill_type='solid'),
              "Team3": PatternFill(start_color='deebf7', end_color='deebf7', fill_type='solid')}
    thin_border = Border(left=Side(style='thin'),
                         right=Side(style='thin'),
                         top=Side(style='thin'),
                         bottom=Side(style='thin'))
    columns = [chr(i + 65) if i < 26 else chr(i // 26 + 64) + chr(i % 26 + 65) for i in
               range(len([day for week in weeks for day in week.days]) + 10)]
    # add Employee Names
    row = 1
    fill_to = len([day for week in weeks for day in week.days]) + 3
    for team in teams:
        for employee in team.employees:
            sheet[f"A{row * 2}"] = str(team)
            sheet[f"B{row * 2}"] = employee.name
            sheet[f"C{row * 2}"] = str([str(skill) for skill in employee.skills]).replace("[", "").replace("]",
                                                                                                           "").replace(
                "'", "")
            for i in range(0, fill_to):
                sheet[f"{columns[i]}{row * 2}"].fill = colors[str(team)]
            row = row + 1

    # add name and skills
    sheet["A1"] = "Team"
    sheet["B1"] = "Name"
    sheet["C1"] = "Skills"

    # add calendar
    wochentage = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    column = 3
    for week in weeks:
        for j in range(1, len(week.days) + 1):
            index = (j - 1)
            sheet[f"{columns[column]}{1}"] = wochentage[index]
            if week.days[index].name == "Sa" or week.days[index].name == "So":
                for i in range(1, len([employee for team in teams for employee in team.employees])*2+1+1):
                    sheet[f"{columns[column]}{i}"].fill = colors["weekend"]
                    sheet[f"{columns[column]}{i}"].border = thin_border
            column = column + 1

    # add results
    for key in model_result.keys():
        if model_result[key]:
            split = key.split("_")
            week, day, shift, team, employee, needed_skill = split[0], split[1], split[2], split[3], split[4], split[5]
            this_column = columns[
                ((wochentage.index(day) + 1) + 7 * (int(re.search(r'week(\d+)', week, re.I).group(1)) - 1) + 2)]
            this_row = ([tmp_employee.name for team in teams for tmp_employee in team.employees].index(
                employee) + 1) * 2
            sheet[
                f"{this_column}{this_row}"
            ] = shift
            sheet[
                f"{this_column}{this_row}"
            ].fill = colors[shift]
            sheet[
                f"{this_column}{this_row}"
            ].border = thin_border
            this_row = this_row + 1
            sheet[
                f"{this_column}{this_row}"
            ] = needed_skill
            sheet[
                f"{this_column}{this_row}"
            ].fill = colors[needed_skill]
            sheet[
                f"{this_column}{this_row}"
            ].border = thin_border
    workbook.save(filename="hello_world.xlsx")