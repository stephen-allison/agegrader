import streamlit as st
import pandas as pd
from enum import Enum
from agegrader.agegrader import power_of_ten_grader, parse_time

class InputMode(Enum):
    CATEGORY = "Category"
    AGE_GENDER = "Age and Gender"


st.set_page_config(
    page_title="Running Age Grader",
    page_icon="🏃‍♂️",  # emoji or image path
    layout="wide",      # "centered" (default) or "wide"
)

# Initialize the age grader
if 'age_grader' not in st.session_state:
    st.session_state.age_grader = power_of_ten_grader()

if 'input_mode' not in st.session_state:
    st.session_state.input_mode = InputMode.CATEGORY

# Streamlit App
st.title("🏃‍♂️ Running Age Grade Calculator")

# Results input section
st.subheader("1. Enter Race Results")

# Sample data creation function
def create_sample_data():
    if st.session_state.input_mode == InputMode.CATEGORY:
        st.session_state.results_df = pd.DataFrame({
            'Name': ['John Smith', 'Jane Doe'],
            'Category': ['SM', 'F40'],
            'Distance': ['10K', '5K'],
            'Time': ['42:30', '22:15'],
            'Age Grade': ['', '']
        })
    else:
        st.session_state.results_df = pd.DataFrame({
            'Name': ['John Smith', 'Jane Doe'],
            'Age': [26, 43],
            'Gender': ['M', 'F'],
            'Distance': ['10K', '5K'],
            'Time': ['42:30', '22:15'],
            'Age Grade': ['', '']
        })

# Initialize sample data if needed
if 'results_df' not in st.session_state:
    create_sample_data()


def mode_changed():
    if 'results_df' in st.session_state:
        del st.session_state.results_df
    # Force recreation of dataframe with correct columns
    create_sample_data()

st.write('**Enter results by Age and Gender or Category:**')
col1, col2 = st.columns([1, 3])
with col1:
    input_mode = st.selectbox(
        'Input Mode:',
        options=[InputMode.CATEGORY, InputMode.AGE_GENDER],
        format_func=lambda x: x.value,
        key='input_mode',
        on_change=mode_changed,
        label_visibility='collapsed',
    )

# Data editor for results
st.write("**Edit the table below** (you can add/remove rows and paste data):")

if st.session_state.input_mode == InputMode.CATEGORY:
    column_config = {
        "Name": st.column_config.TextColumn("Runner Name"),
        "Category": st.column_config.TextColumn("Category"),
        "Distance": st.column_config.SelectboxColumn(
            "Distance",
            options=st.session_state.age_grader.discipline_to_heading.keys() ,
            required=True
        ),
        "Time": st.column_config.TextColumn(
            "Time (MM:SS or H:MM:SS)",
            help="Format: 42:30 or 1:25:30"
        ),
        "Age Grade": st.column_config.TextColumn(
            "Age Grade %",
            disabled=True
        )
    }
else:
    column_config = {
        "Name": st.column_config.TextColumn("Runner Name"),
        "Age": st.column_config.NumberColumn("Age", min_value=5, max_value=100),
        "Gender": st.column_config.SelectboxColumn(
            'Gender',
            options=['M', 'F'],
            required=True
        ),
        "Distance": st.column_config.SelectboxColumn(
            "Distance",
            options=st.session_state.age_grader.discipline_to_heading.keys(),
            required=True
        ),
        "Time": st.column_config.TextColumn(
            "Time (MM:SS or H:MM:SS)",
            help="Format: 42:30 or 1:25:30"
        ),
        "Age Grade": st.column_config.TextColumn(
            "Age Grade %",
            disabled=True
        )
    }

edited_df = st.data_editor(
    st.session_state.results_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config=column_config
)

# Calculate button
if st.button("🧮 Calculate Age Grades", type="primary"):
    # Calculate age grades for each row
    for idx, row in edited_df.iterrows():
        if pd.notna(row['Time']) and row['Time'] != '':
            time_seconds = parse_time(row['Time'])
            if time_seconds > 0:
                # Check which columns are available to determine mode
                if 'Category' in row and pd.notna(row['Category']):
                    age_grade = st.session_state.age_grader.get_age_grade_by_category(
                        row['Distance'],
                        row['Category'],
                        time_seconds
                    )
                elif 'Age' in row and 'Gender' in row and pd.notna(row['Age']) and pd.notna(row['Gender']):
                    age_grade = st.session_state.age_grader.get_age_grade(
                        row['Distance'],
                        row['Gender'],
                        int(row['Age']),
                        time_seconds
                    )
                else:
                    continue  # Skip row if missing required data
                
                formatted_grade = f"{age_grade:.2f}%"
                edited_df.at[idx, 'Age Grade'] = formatted_grade
                print('Graded:', row['Name'], row['Distance'], row['Time'], formatted_grade)

    # Update session state
    st.session_state.results_df = edited_df

    # Display results
    st.subheader("📊 Results with Age Grades")
    st.dataframe(edited_df, use_container_width=True, hide_index=True)

    # Download results
    csv = edited_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv,
        file_name="age_graded_results.csv",
        mime="text/csv"
    )

# Instructions
with st.expander("ℹ️ How to use this app"):
    st.markdown("""
        1. **Choose input mode**: Select "Age and Gender" (separate columns) or "Category" (combined like M45, F30)
        2. **Enter results**: Add runner data in the table below
           - **Name**: Runner's name
           - **Age/Gender or Category**: 
             - Age and Gender mode: Separate age (5-100) and gender (M/F) columns
             - Category mode: Combined format like M45, F30, Senior, etc.
           - **Distance**: Race distance (5K, 10K, HM, Marathon, etc.)
           - **Time**: Race time in MM:SS or H:MM:SS format (e.g., 42:30 or 1:25:30)
        3. **Calculate**: Click the button to calculate age grades
        4. **Download**: Export results as CSV

        **Tips:**
        - You can copy/paste data from spreadsheets directly into the table
        - Switching between modes will reset the table with sample data
        - Age grade shows how your performance compares to world standards for your age/gender
        - Higher percentages = better relative performance
        - Uses 2015 WMA (World Masters Athletics) age grading standards
        """)

# Show available distances
with st.expander("📏 Available Distances"):
    distances = st.session_state.age_grader.discipline_to_heading.keys()
    st.write(", ".join(sorted(distances)))

with st.expander("🙏 Credits"):
    st.markdown('''
    **WAVA Standards**
    Compiled by Alan Jones, 3717 Wildwood Drive, Endwell, NY 13760, 607-786-5866
    
    AlanLJones@stny.rr.com, http://runscore.com/Alan/AgeGrade.html
    
    With lots of help from Rex Harvey
    
    January 2015
    
    Running Age-Grade Tables are licensed under a Creative Commons Attribution 4.0 International License: http://creativecommons.org/licenses/by/4.0/
    ''')