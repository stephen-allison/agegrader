import pytest
from agegrader import power_of_ten_grader

def hms_to_s(h = 0, m = 0, s = 0):
    return (h * 3600) + (m * 60) + s

@pytest.fixture
def grader():
    return power_of_ten_grader()

SUMMER_LEAGUE_5M_RESULTS = [
    ('M45', hms_to_s(m=32, s=24), 71.35),
    ('F35', hms_to_s(m=35, s=47), 68.10),
    ('M50', hms_to_s(m=40, s=4), 60.07),
    ('F40', hms_to_s(m=45, s=15), 55.03),
    ('SF', hms_to_s(m=37, s=7), 65.20),
    ('SM', hms_to_s(m=37, s=19), 57.12),
    ('FU17', hms_to_s(h=1, m=11, s=7), 34.87),
    ('MU17', hms_to_s(m=31, s=30), 68.25)
]

@pytest.mark.parametrize('category, time, expected_grade', SUMMER_LEAGUE_5M_RESULTS)
def test_age_grading(grader, category, time, expected_grade):
    grade = grader.get_age_grade_by_category('5M', category, time)
    assert grade == expected_grade


AGE_AND_GENDER_RESULTS = [
    (26, 'M', '5K', hms_to_s(m=20, s=0), 64.92),
    (56, 'M', '5K', hms_to_s(m=22, s=0), 70.23),
    (43, 'M', '10M', hms_to_s(h=1, m=10, s=7), 66.25),
    (12, 'F', '5K', hms_to_s(m=21, s=56), 75.15),
    (29, 'F', 'HM', hms_to_s(m=100, s=17), 65.02),
    (48, 'F', 'Mar', hms_to_s(h=2, m=58), 84.38)
]

@pytest.mark.parametrize('age, gender, distance, time, expected_grade', AGE_AND_GENDER_RESULTS)
def test_age_grading(grader, age, gender, distance, time, expected_grade):
    grade = grader.get_age_grade(distance, gender, age, time)
    assert grade == expected_grade

