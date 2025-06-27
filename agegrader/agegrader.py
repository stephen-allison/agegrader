import pandas as pd
import re

# Constants
MARATHON_LENGTH = 42.194988
MILE_IN_KM = 1.609344

# Standard distances for reference
standard_distance_names = ["3km", "5km", "5 miles", "10km", "10 miles", "A half marathon", "A marathon", "(Other)"]
standard_distances = [3, 5, 5 * MILE_IN_KM, 10, 10 * MILE_IN_KM, MARATHON_LENGTH * 0.5, MARATHON_LENGTH, "other"]


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


def parse_time(time_str, distance_km):
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

    def __init__(self, male_file_path='lib/MaleRoadStd2015.xlsx', female_file_path='lib/FemaleRoadStd2015.xlsx'):
        # Map from gender code to DataFrame of data
        self.gender_to_data = {}
        # Map from gender code to column mappings
        self.heading_to_index = {}

        # Map from Power of 10 codes to codes in spreadsheet
        self.discipline_to_heading = {
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

        # Load the Excel files
        self.process_xlsx('M', male_file_path)
        self.process_xlsx('F', female_file_path)
        self.loaded = True

    def process_xlsx(self, gender, file_path):
        """Process Excel file and store data for given gender"""
        try:
            # Read from sheet 2 (index 1), equivalent to PHP's $xlsx->rows(2)
            df = pd.read_excel(file_path, sheet_name=1, skiprows=1)
            self.gender_to_data[gender] = df

            # Create column name to index mapping
            headings = df.columns.tolist()
            column_map = {heading: i for i, heading in enumerate(headings)}
            self.heading_to_index[gender] = column_map

        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            self.gender_to_data[gender] = None
            self.heading_to_index[gender] = {}

    def get_heading(self, discipline):
        """Get the spreadsheet column heading for a discipline"""
        # Remove suffixes
        discipline = re.sub(r'NAD$', '', discipline)
        discipline = re.sub(r'XC$', '', discipline)
        discipline = re.sub(r'MT$', '', discipline)

        return self.discipline_to_heading.get(discipline, False)

    def supports_discipline(self, discipline):
        """Check if the discipline is supported"""
        return self.get_heading(discipline) is not False

    def get_standard(self, discipline, gender, age):
        """Get the age graded standard in seconds"""
        heading = self.get_heading(discipline)
        if heading is False:
            return False

        if gender not in self.gender_to_data:
            return False

        if age < 0:
            return False

        df = self.gender_to_data[gender]
        if df is None:
            return False

        # Clamp age to valid range
        age = max(5, min(100, age))

        # Age corresponds to row index (age 5 = row 0, age 6 = row 1, etc.)
        row_index = age - 3

        if row_index >= len(df) or heading not in df.columns:
            return False

        try:
            value = df.iloc[row_index][heading]
            if pd.isna(value) or value == '':
                return False
            return float(value)
        except (ValueError, IndexError):
            return False

    def age_from_category(self, category):
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

    def gender_from_category(self, category):
        if category.startswith(('F', 'VF', 'VW', 'SF', 'SW', 'JW', 'JF', 'JG')):
            return 'F'
        elif category.startswith(('M', 'VM', 'SM', 'JM', 'JB')):
            return 'M'

    def get_age_grade(self, discipline, gender, age, time_seconds):
        """Calculate age grading percentage"""
        standard = self.get_standard(discipline, gender, age)
        if standard is False:
            return ""

        percentage = (standard / time_seconds) * 100
        return f"{percentage:.2f}%"

    def get_age_grade_by_category(self, discipline, category, time_seconds):
        cat_age = self.age_from_category(category)
        gender = self.gender_from_category(category)
        return self.get_age_grade(discipline, gender, cat_age, time_seconds)


# Example usage
if __name__ == "__main__":
    # Create age grader instance
    grader = AgeGrader()

    # Example: 45-year-old male runs 10K in 40 minutes (2400 seconds)
    result = grader.get_age_grade_by_category('5M', 'M', 'M45', (29*60)+2)
    print(f"Age grading (mk): {result}")

    result = grader.get_age_grade_by_category('5M', 'M', 'M45', (37*60)+34)
    print(f"Age grading (cl): {result}")

    result = grader.get_age_grade_by_category('5M', 'M', 'M50', 1628)
    print(f"Age grading (am): {result}")

    result = grader.get_age_grade_by_category('5M', 'M', 'M50', (40*60)+4)
    print(f"Age grading (sa): {result}")

    result = grader.get_age_grade_by_category('5M', 'F', 'SF', (37*60)+7)
    print(f"Age grading (dn): {result}")

    result = grader.get_age_grade_by_category('Marathon', 'F', 'F50', (41*60) + 43)
    print(f"Age grading (cw): {result}")

    # Test time formatting
    print(f"2400 seconds formatted: {format_time(2400)}")

    # Test time parsing
    parsed = parse_time("40:00", 10)
    print(f"40:00 parsed to seconds: {parsed}")
