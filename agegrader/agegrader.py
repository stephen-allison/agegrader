import re
from .combined_standards import STANDARDS

# Constants
MARATHON_LENGTH = 42.194988
MILE_IN_KM = 1.609344

# Standard distances for reference
standard_distance_names = ["3km", "5km", "5 miles", "10km", "10 miles", "A half marathon", "A marathon", "(Other)"]
standard_distances = [3, 5, 5 * MILE_IN_KM, 10, 10 * MILE_IN_KM, MARATHON_LENGTH * 0.5, MARATHON_LENGTH, "other"]

# Map from discipline names used in power of 10 export to the names used in the standards spreadsheet
POWER_OF_TEN_DISCIPLINE_MAP = {
    'parkrun': '5 km',
    '5K': '5 km',
    '6K': '6 km',
    '4M': '4 Mile',
    '8K': '8 km',
    '5M': '5 Mile',
    '10K': '10 km',
    '12K': '12 km',
    '15K': '15 km',
    '10M': '10 Mile',
    '20K': '20 km',
    'HM': 'H. Mar',
    '25K': '25 km',
    '30K': '30 km',
    'Mar': 'Marathon',
    '50K': '50 km',
    '50M': '50 Mile',
    '100K': '100 km',
    '150K': '150 km',
    '100M': '100 Mile',
    '200K': '200 km'
}


def format_time(seconds):
    """Format seconds into HH:MM:SS or MM:SS or SS format"""
    seconds = int(seconds + 0.5)
    s = seconds % 60
    m1 = seconds // 60
    m = m1 % 60
    h = m1 // 60

    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    elif m > 0:
        return f"{m}:{s:02d}"
    else:
        return f"{s}"


def parse_time(time_str):
    """Parse a user entered time as time in seconds"""
    time_list = time_str.split(':')

    if len(time_list) == 2:
        h, m, s = 0, int(time_list[0]), int(time_list[1])
    elif len(time_list) == 3:
        h, m, s = int(time_list[0]), int(time_list[1]), int(time_list[2])
    else:
        return None

    return h * 3600 + m * 60 + s


class AgeGrader:
    """An Age Grader instance is used to compute age gradings."""

    def __init__(self, standards, discipline_to_heading_map):
        self.standards = standards
        # Map from discipline names to headings from standards spreadsheet
        self.discipline_to_heading = discipline_to_heading_map

    def _get_heading(self, discipline):
        """Get the spreadsheet column heading for a discipline"""
        # Remove suffixes
        discipline = re.sub(r'NAD$', '', discipline)
        discipline = re.sub(r'XC$', '', discipline)
        discipline = re.sub(r'MT$', '', discipline)

        if discipline in self.discipline_to_heading.values():
            return discipline
        return self.discipline_to_heading.get(discipline)

    def _get_standard(self, discipline, gender, age):
        """Get the age graded standard in seconds"""
        heading = self._get_heading(discipline)

        if not heading:
            return False

        if gender not in self.standards:
            return False

        # Clamp age to valid range
        age = max(5, min(100, age))

        try:
            value = self.standards[gender][heading][age - 5]
            return float(value)
        except KeyError:
            return False

    def _age_from_category(self, category):
        """Extract age from category string like 'M45' or 'Senior'"""
        if 'Senior' in category or 'SM' in category or 'SF' in category:
            return 21

        # Try extracting numeric part after first character
        age_str = category[1:]
        if age_str.isdigit():
            return int(age_str)

        # Try extracting numeric part after first two characters
        age_str = category[2:]
        if age_str.isdigit():
            return int(age_str)

        return -1

    def _gender_from_category(self, category):
        if category.startswith(('F', 'VF', 'VW', 'SF', 'SW', 'JW', 'JF', 'JG')):
            return 'F'
        elif category.startswith(('M', 'VM', 'SM', 'JM', 'JB')):
            return 'M'
        return None

    def get_age_grade(self, discipline, gender, age, time_seconds):
        """Calculate age grading percentage"""
        standard = self._get_standard(discipline, gender, age)
        if standard is False:
            return ""

        percentage = (standard / time_seconds) * 100
        return round(percentage, 2)

    def get_age_grade_by_category(self, discipline, category, time_seconds):
        cat_age = self._age_from_category(category)
        gender = self._gender_from_category(category)
        return self.get_age_grade(discipline, gender, cat_age, time_seconds)


def power_of_ten_grader(year=2015):
    return AgeGrader(STANDARDS[str(year)], POWER_OF_TEN_DISCIPLINE_MAP)
