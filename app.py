import streamlit as st
from clinical_trials_app import fetch_studies, process_studies, sanitize_text
from mapbox_api import get_location_suggestions  
import pandas as pd
import json

st.title("Clinical Trials Search")
condition = st.text_input("Condition/Disease", value="cancer")
other_terms = st.text_input("Other Terms", value="treatment")
user_input = st.text_input('Type a location (city, state)', value="new york")
if user_input:
    suggestions = get_location_suggestions(user_input)
    selected_location = st.selectbox('Select a location:', suggestions)
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
    results = fetch_studies(condition, other_terms, selected_location, status, min_age, max_age, page_size)
    if results and 'studies' in results:
        df = process_studies(results)
        df['Title'] = df['Title'].apply(sanitize_text)
        df['Eligibility Criteria'] = df['Eligibility Criteria'].apply(sanitize_text)
        st.dataframe(df.head(page_size+1))

        csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(label="Download data as CSV", data=csv, file_name='clinical_trials.csv', mime='text/csv')
        
       
        json_data = json.dumps(results, indent=2)  
        st.download_button(label="Download data as JSON", data=json_data, file_name='clinical_trials.json', mime='application/json')
    else:
        st.error("No results found or error fetching data.")
