"""
Convert age grading Excel files to dictionary structure
"""
import pandas as pd
import json

'''
Extracts the baseline times from XLSX sheets found here: 
https://github.com/AlanLyttonJones/Age-Grade-Tables/tree/master

Expects the files to be in the 'data' directory.
Writes the python module agegrader.combined_standards.py which is then used in the application
'''

def excel_to_dict(file_path, drop_leading_values=2):
    """
    Convert Excel file (sheet 2) to dictionary structure where:
    - Keys are distance column headers
    - Values are lists of times for all ages
    """
    try:
        # Read from sheet 2 (index 1), skip first row like the original code
        df = pd.read_excel(file_path, sheet_name=1, skiprows=1)

        result = {}

        # Iterate through each column
        for column in df.columns:
            # Skip non-distance columns (like Age, if present)
            if any(skip_word in str(column).lower() for skip_word in ['age', 'unnamed']):
                continue

            # Get all values in this column, excluding NaN/empty values
            times = []
            for value in df[column]:
                if pd.notna(value) and value != '':
                    try:
                        # Convert to float if possible, otherwise keep as string
                        times.append(float(value))
                    except (ValueError, TypeError):
                        times.append(str(value))

            # Use column name as key
            if times:  # Only add if we have data
                result[str(column)] = times[drop_leading_values:]

        # Print summary
        print(f"\nProcessed {file_path}:")
        print(f"Found {len(result)} distance columns")
        for distance, times in result.items():
            print(f"  {distance}: {len(times)} times")

        return result

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return {}


def extract_standard_times(standards_year, female_standards_file, male_standards_file, drop_leading_values):
    # Process male standards
    male_dict = excel_to_dict(male_standards_file, drop_leading_values)
    # Process female standards
    female_dict = excel_to_dict(female_standards_file, drop_leading_values)
    # Create combined structure
    combined = {
        'M': male_dict,
        'F': female_dict
    }
    return combined

def standards_for_year(year, male_standards_file, female_standards_file, drop_leading_values=2):
    """Process both male and female standards files"""

    print("Converting Excel files to dictionary structure...")
    combined_standards = extract_standard_times(year, female_standards_file, male_standards_file, drop_leading_values)

    # Show sample of structure
    print("\nSample structure:")
    if 'M' in combined_standards:
        male_dict = combined_standards['M']
        first_distance = list(male_dict.keys())[0]
        print(f"Male {first_distance}: {male_dict[first_distance][:5]}... (showing first 5)")

    return combined_standards


def process_standards(*specs):
    results = {}
    for spec in specs:
        for_year = standards_for_year(**spec)
        results[spec['year']] = for_year
    write(results, 'agegrader/combined_standards.py')


def write(result, output_name):
    # Save to JSON file if output name provided
    if output_name:
        with open(f"{output_name}", 'w') as f:
            data = json.dumps(result, indent=2)
            file_contents = f'STANDARDS = {data}'
            f.write(file_contents)
        print(f"Saved to {output_name}.json")


if __name__ == "__main__":
    '''
    settings for each year's standards:
    'year': the year of the data (int)
    'male_standards_file': the path to the male standards file (str)
    'female_standards_file': the path to the female standards file (str)
    'drop_leading_values': the number of leading values to drop from each time column, i.e those leading values that are not actually times
    '''
    standards_2015 = {'year': 2015,
                      'male_standards_file': 'data/MaleRoadStd2015.xlsx',
                      'female_standards_file': 'data/FemaleRoadStd2015.xlsx',
                      'drop_leading_values': 2}

    standards_2025 = {'year': 2025,
                      'male_standards_file': 'data/MaleRoadStd2025.xlsx',
                      'female_standards_file': 'data/FemaleRoadStd2025.xlsx',
                      'drop_leading_values': 3}

    process_standards(standards_2015, standards_2025)
