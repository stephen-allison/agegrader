import pytest
from agegrader import power_of_ten_grader

def hms_to_s(h = 0, m = 0, s = 0 ):
    return (h * 3600) + (m * 60) + s

@pytest.fixture
def grader():
    return power_of_ten_grader()

SUMMER_LEAGUE_5M_RESULTS = [
    ('M45', hms_to_s(m=32, s=24), 71.35),
    ('F35', hms_to_s(m=35, s=47), 68.10),
    ('M50', hms_to_s(m=40, s=4), 60.07),
    ('F40', hms_to_s(m=45, s=15), 55.03)
]

@pytest.mark.parametrize('category, time, expected_grade', SUMMER_LEAGUE_5M_RESULTS)
def test_age_grading(grader, category, time, expected_grade):
    grade = grader.get_age_grade_by_category('5M', category, time)
    assert grade == expected_grade


