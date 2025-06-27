"""
Convert age grading Excel files to dictionary structure
"""
import pandas as pd
import json


def excel_to_dict(file_path, output_name=None):
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
                result[str(column)] = times

        # Print summary
        print(f"\nProcessed {file_path}:")
        print(f"Found {len(result)} distance columns")
        for distance, times in result.items():
            print(f"  {distance}: {len(times)} times")

        # Save to JSON file if output name provided
        if output_name:
            with open(f"{output_name}.json", 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Saved to {output_name}.json")

        return result

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return {}


def process_both_files():
    """Process both male and female standards files"""

    print("Converting Excel files to dictionary structure...")

    # Process male standards
    male_dict = excel_to_dict('lib/MaleRoadStd2015.xlsx', 'male_standards')

    # Process female standards
    female_dict = excel_to_dict('lib/FemaleRoadStd2015.xlsx', 'female_standards')

    # Create combined structure
    combined = {
        'M': male_dict,
        'F': female_dict
    }

    # Save combined file
    with open('agegrader/combined_standards.py', 'w') as f:
        json.dump(combined, f, indent=2)

    print(f"\nCombined structure saved to combined_standards.py")

    # Show sample of structure
    print("\nSample structure:")
    if male_dict:
        first_distance = list(male_dict.keys())[0]
        print(f"Male {first_distance}: {male_dict[first_distance][:5]}... (showing first 5)")

    return combined


def inspect_excel_structure(file_path):
    """Helper function to inspect Excel file structure"""
    print(f"\nInspecting {file_path}:")

    try:
        # Check all sheets
        excel_file = pd.ExcelFile(file_path)
        print(f"Available sheets: {excel_file.sheet_names}")

        # Look at sheet 2 structure
        df = pd.read_excel(file_path, sheet_name=1, skiprows=1)
        print(f"Sheet 2 shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"First few rows:")
        print(df.head())

    except Exception as e:
        print(f"Error inspecting {file_path}: {e}")


if __name__ == "__main__":
    # You can run this script directly

    # First, inspect the files to see their structure
    print("=== INSPECTING FILE STRUCTURE ===")
    inspect_excel_structure('lib/MaleRoadStd2015.xlsx')
    inspect_excel_structure('lib/FemaleRoadStd2015.xlsx')

    print("\n=== CONVERTING TO DICTIONARY ===")
    # Process both files
    result = process_both_files()

    # Show available distances
    if result and 'M' in result:
        print(f"\nAvailable distances: {list(result['M'].keys())}")