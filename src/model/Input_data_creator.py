from src.model.Day import Day
from src.model.Employee import Employee
from src.model.Shift import Shift
from src.model.Skill import Skill
from src.model.Team import Team
from src.model.Week import Week


def create_input_data(number_of_days: int) -> tuple[list[Week], list[Team]]:
    # create Skills
    skills: dict[str, Skill] = {"MO:M1": Skill("MO:M1"),
                                "H1:M1": Skill("H1:M1"),
                                "H2:M1": Skill("H2:M1"),
                                "H:M2": Skill("H:M2"),
                                "MO:M3": Skill("MO:M3"),
                                "H:M3": Skill("H:M3"),
                                "MO:M4": Skill("MO:M4")}
    helper = [skills["H1:M1"], skills["H2:M1"], skills["H:M2"], skills["H:M3"]]
    teams: list[Team] = []
    # Team 1
    employees: list[Employee] = [Employee("P1", [skills["MO:M1"], skills["MO:M3"]] + helper, is_shift_manager=True),
                                 Employee("P2", [skills["MO:M3"]] + helper),
                                 Employee("P3", [skills["MO:M1"], skills["MO:M3"]] + helper),
                                 Employee("P4", [skills["H:M3"]]),
                                 Employee("P5", helper),
                                 Employee("P6", [skills["MO:M1"], skills["MO:M3"]] + helper, is_shift_manager=True),
                                 Employee("P7", helper),
                                 Employee("P8", helper),
                                 Employee("P9", helper),
                                 Employee("P10", helper),
                                 Employee("P11", helper),
                                 Employee("P12", [skills["MO:M4"]] + helper)]
    teams.append(Team("Team1", employees))
    # Team 2
    employees: list[Employee] = [Employee("P13", [skills["MO:M1"], skills["MO:M3"]] + helper, is_shift_manager=True),
                                 Employee("P14", [skills["MO:M1"], skills["MO:M3"]] + helper),
                                 Employee("P15", helper),
                                 Employee("P16", [skills["MO:M1"], skills["MO:M3"]] + helper),
                                 Employee("P17", [skills["MO:M1"], skills["MO:M3"]] + helper, is_shift_manager=True),
                                 Employee("P18", helper),
                                 Employee("P19", helper),
                                 Employee("P20", [skills["MO:M1"], skills["MO:M3"]] + helper),
                                 Employee("P21", helper),
                                 Employee("P22", helper),
                                 Employee("P23", [skills["MO:M3"], skills["MO:M4"]] + helper)]
    teams.append(Team("Team2", employees))
    # Team 3
    employees: list[Employee] = [Employee("P24", [skills["MO:M1"], skills["MO:M3"]] + helper, is_shift_manager=True),
                                 Employee("P25", helper),
                                 Employee("P26", [skills["MO:M1"], skills["MO:M3"]] + helper),
                                 Employee("P27", helper),
                                 Employee("P28", helper),
                                 Employee("P29", helper),
                                 Employee("P30", [skills["MO:M1"], skills["MO:M3"]] + helper, is_shift_manager=True),
                                 Employee("P31", [skills["MO:M1"], skills["MO:M3"]] + helper),
                                 Employee("P32", helper),
                                 Employee("P33", helper),
                                 Employee("P34", [skills["MO:M4"]] + helper)]
    teams.append(Team("Team3", employees))

    skills_m1: list[Skill] = [skills["MO:M1"], skills["H1:M1"], skills["H2:M1"]]
    skills_m2: list[Skill] = [skills["H:M2"]]
    skills_m3: list[Skill] = [skills["MO:M3"], skills["H:M3"]]
    skills_m4: list[Skill] = [skills["MO:M4"]]

    # create days and shifts
    days: list[Day] = []
    days.append(Day("Mo",
                    [Shift("M", skills_m1 + skills_m3 + skills_m4),
                     Shift("A", skills_m1 + skills_m2 + skills_m3 + skills_m4),
                     Shift("N", skills_m1 + skills_m2 + skills_m3 + skills_m4)]))
    days.append(Day("Tu",
                    [Shift("M", skills_m1 + skills_m2 + skills_m3 + skills_m4),
                     Shift("A", skills_m1 + skills_m2 + skills_m3 + skills_m4),
                     Shift("N", skills_m1 + skills_m2 + skills_m3 + skills_m4)]))
    days.append(Day("We",
                    [Shift("M", skills_m1 + skills_m2 + skills_m3 + skills_m4),
                     Shift("A", skills_m1 + skills_m2 + skills_m3 + skills_m4),
                     Shift("N", skills_m1 + skills_m2 + skills_m3 + skills_m4)]))
    days.append(Day("Th",
                    [Shift("M", skills_m1 + skills_m2 + skills_m3 + skills_m4),
                     Shift("A", skills_m1 + skills_m2 + skills_m3 + skills_m4),
                     Shift("N", skills_m1 + skills_m2 + skills_m3 + skills_m4)]))
    days.append(Day("Fr",
                    [Shift("M", skills_m1 + skills_m2 + skills_m3 + skills_m4),
                     Shift("A", skills_m1 + skills_m2 + skills_m3 + skills_m4),
                     Shift("N", skills_m1 + skills_m2 + skills_m3 + skills_m4)]))
    days.append(Day("Sa",
                    [Shift("M", skills_m1 + skills_m2 + skills_m3),
                     Shift("A", skills_m1 + skills_m3),
                     Shift("N", skills_m1 + skills_m3)]))
    days.append(Day("Su",
                    [Shift("M", skills_m1 + skills_m3),
                     Shift("A", skills_m1 + skills_m3),
                     Shift("N", skills_m1 + skills_m3)]))

    weeks = []
    days_for_week = []
    i = 0
    while i < number_of_days:
        if i % 7 == 0 and i != 0:
            weeks.append(Week(f"Week{i//7}", days_for_week))
            days_for_week = []
        days_for_week.append(days[i % 7])
        i += 1
    if i % 7 != 0:
        weeks.append(Week(f"Week{i//7+1}", days_for_week))

    return weeks, teams
