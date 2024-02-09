import streamlit as st
from clinical_trials_app import fetch_studies, process_studies
import pandas as pd

# Streamlit UI setup with predefined inputs
st.title("Clinical Trials Search")
condition = st.text_input("Condition/Disease", value="cancer")
other_terms = st.text_input("Other Terms", value="treatment")
location = st.text_input("Location", value="new york")
status = st.selectbox("Status", ["RECRUITING", "NOT_YET_RECRUITING", "COMPLETED"], index=0)
age_group = st.selectbox("Age Group", ["Child (birth–17)", "Adult (18–64)", "Older Adult (65+)"], index=1)
page_size = st.number_input("Results to display", min_value=10, max_value=100, value=10)

# Map age group to min/max age for the API call
age_mapping = {
    "Child (birth–17)": {"min_age": "0 years", "max_age": "17 years"},
    "Adult (18–64)": {"min_age": "18 years", "max_age": "64 years"},
    "Older Adult (65+)": {"min_age": "65 years", "max_age": "120 years"}
}
min_age, max_age = age_mapping[age_group]["min_age"], age_mapping[age_group]["max_age"]

if st.button("Search Clinical Trials"):
    # Fetch and process the clinical trials data
    print("fetching data")
    print(type(condition), type(other_terms), type(location), type(status), type(min_age), type(max_age), type(page_size))
    results = fetch_studies(condition, other_terms, location, status, min_age, max_age, page_size)
    if results and 'studies' in results:
        df = process_studies(results)
        st.dataframe(df.head(page_size))
        # Include download buttons for CSV/JSON as needed
    else:
        st.error("No results found or error fetching data.")
