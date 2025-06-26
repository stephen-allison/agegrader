import streamlit as st
import pandas as pd
from agegrader.agegrader import AgeGrader, parse_time

# Initialize the age grader
if 'age_grader' not in st.session_state:
    st.session_state.age_grader = AgeGrader()

# Streamlit App
st.title("🏃‍♂️ Running Age Grade Calculator")

# Results input section
st.subheader("1. Enter Race Results")

# Sample data for the table
if 'results_df' not in st.session_state:
    st.session_state.results_df = pd.DataFrame({
        'Name': ['John Smith', 'Jane Doe'],
        'Category': ['SM', 'F40'],
        'Distance': ['10K', '5K'],
        'Time': ['42:30', '22:15'],
        'Age Grade': ['', '']
    })

# Data editor for results
st.write("**Edit the table below** (you can add/remove rows and paste data):")

edited_df = st.data_editor(
    st.session_state.results_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Name": st.column_config.TextColumn("Runner Name"),
        "Category": st.column_config.TextColumn("Category"),
        "Distance": st.column_config.SelectboxColumn(
            "Distance",
            options=["5K", "10K", "15K", "HM", "Half Marathon", "Marathon", "5M", "10M"],
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
)

# Calculate button
if st.button("🧮 Calculate Age Grades", type="primary"):
    if not getattr(st.session_state.age_grader, 'loaded', False):
        st.error("❌ Please upload the age grading standards files first!")
    else:
        # Calculate age grades for each row
        for idx, row in edited_df.iterrows():
            if pd.notna(row['Time']) and row['Time'] != '':
                time_seconds = parse_time(row['Time'], 10)
                print(row)
                if time_seconds > 0:
                    age_grade = st.session_state.age_grader.get_age_grade_by_category(
                        row['Distance'],
                        row['Category'],
                        time_seconds
                    )
                    print('ag', age_grade)
                    edited_df.at[idx, 'Age Grade'] = age_grade

        # Update session state
        st.session_state.results_df = edited_df

        # Display results
        st.subheader("📊 Results with Age Grades")
        st.dataframe(edited_df, use_container_width=True)

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
    1. **Enter results**: Add runner data in the table below
       - **Name**: Runner's name
       - **Gender**: M or F
       - **Age**: Age in years (5-100)
       - **Distance**: Race distance (5K, 10K, HM, Marathon, etc.)
       - **Time**: Race time in MM:SS or H:MM:SS format (e.g., 42:30 or 1:25:30)
    2. **Calculate**: Click the button to calculate age grades
    3. **Download**: Export results as CSV

    **Tips:**
    - You can copy/paste data from spreadsheets directly into the table
    - Age grade shows how your performance compares to world standards for your age/gender
    - Higher percentages = better relative performance
    - Uses 2015 WMA (World Masters Athletics) age grading standards
    """)

# Show available distances
if getattr(st.session_state.age_grader, 'loaded', False):
    with st.expander("📏 Available Distances"):
        distances = st.session_state.age_grader.discipline_to_heading.keys()
        st.write(", ".join(sorted(distances)))