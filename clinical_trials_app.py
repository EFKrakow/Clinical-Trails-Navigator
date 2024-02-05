import streamlit as st
import requests
import json
import pandas as pd
import io

def map_age_group_to_query(age_group):
    # Mapping age groups to the API's advanced filtering syntax
    age_queries = {
        "Child (birth–17)": "AREA[MinimumAge]RANGE[MIN, 17 years] AND AREA[MaximumAge]RANGE[17 years, MAX]",
        "Adult (18–64)": "AREA[MinimumAge]RANGE[18 years, 64 years] AND AREA[MaximumAge]RANGE[18 years, 64 years]",
        "Older Adult (65+)": "AREA[MinimumAge]RANGE[65 years, MAX] AND AREA[MaximumAge]RANGE[65 years, MAX]"
    }
    return age_queries.get(age_group, "")

# Function to get clinical trials data with expanded parameters
def get_clinical_trials_data(condition, location, status, study_type, gender, age_group, max_studies=50):
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    all_studies = []
    params = {
        "format": "json",
        "pageSize": 10,
        "query.cond": condition,
        "query.term": age_group,  # Adjust based on correct API usage
        "query.locn": location,
        "filter.overallStatus": status,
        "postFilter.overallStatus": status  # Ensure consistency in status filtering
    }

    age_query = map_age_group_to_query(age_group)
    if age_query:
        params["postFilter.advanced"] = age_query
    
    # Adjusting study_type and gender parameters based on user input
    if study_type != "All":
        params["filter.studyType"] = study_type
    if gender != "All":
        params["filter.gender"] = gender

    page_token = None
    while len(all_studies) < max_studies:
        if page_token:
            params["pageToken"] = page_token

        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            studies = data.get('studies', [])
            all_studies.extend(studies)
            page_token = data.get('nextPageToken')
            if not page_token or len(all_studies) >= max_studies:
                break
        else:
            st.error(f"Failed to retrieve data: {response.status_code}")
            return []

    return all_studies




# Function to process all studies
def process_all_studies(data):
    processed_studies = []

    for study in data:
        protocol_section = study['protocolSection']
        identification = protocol_section['identificationModule']
        status = protocol_section['statusModule']
        design = protocol_section['designModule']
        eligibility = protocol_section['eligibilityModule']
        contacts_locations = protocol_section.get('contactsLocationsModule', {})

        study_info = {
            'Title': identification.get('briefTitle', 'N/A'),
            'Phase': design.get('phases', ['N/A'])[0],
            'Eligibility Criteria': eligibility.get('eligibilityCriteriaText', 'N/A'),
            'Link': f"https://clinicaltrials.gov/ct2/show/{identification.get('nctId', '')}",
            'Status': status.get('overallStatus', 'N/A'),
            'Central Contacts': [],
            'Locations': []
        }

        # Extract central contacts
        central_contacts = contacts_locations.get('centralContactList', [])
        for contact in central_contacts:
            contact_info = contact.get('centralContact', {})
            study_info['Central Contacts'].append({
                'Name': contact_info.get('centralContactName', 'N/A'),
                'Role': contact_info.get('centralContactRole', 'N/A'),
                'Phone': contact_info.get('centralContactPhone', 'N/A'),
                'Email': contact_info.get('centralContactEMail', 'N/A')
            })

        # Extract location details
        locations = contacts_locations.get('locationList', [])
        for location in locations:
            location_info = location.get('location', {})
            location_detail = {
                'Facility': location_info.get('locationFacility', 'N/A'),
                'City': location_info.get('locationCity', 'N/A'),
                'State': location_info.get('locationState', 'N/A'),
                'Country': location_info.get('locationCountry', 'N/A'),
                'Contacts': []
            }

            study_info['Locations'].append(location_detail)

        processed_studies.append(study_info)

    return processed_studies


def convert_to_dataframe(data):
    flattened_data = []
    for study in data:
        if study['Locations']:  # Check if there are any locations listed
            for location in study['Locations']:
                flattened_data.append({
                    'Title': study['Title'],
                    'Phase': study['Phase'],
                    'Eligibility Criteria': study['Eligibility Criteria'],
                    'Link': study['Link'],
                    'Status': study['Status'],
                    'Facility': location['Facility'],
                    'City': location['City'],
                    'State': location['State'],
                    'Country': location['Country']
                })
        else:  # If no locations, still add the study info without location details
            flattened_data.append({
                'Title': study['Title'],
                'Phase': study['Phase'],
                'Eligibility Criteria': study['Eligibility Criteria'],
                'Link': study['Link'],
                'Status': study['Status'],
                'Facility': 'N/A',
                'City': 'N/A',
                'State': 'N/A',
                'Country': 'N/A'
            })
    return pd.DataFrame(flattened_data)


def main():
    st.title("Clinical Trials Finder")

    # Pre-filling the input boxes with default values
    condition = st.text_input("Condition", value="Acute myeloid leukemia")
    status = st.selectbox("Status", ["RECRUITING", "NOT_YET_RECRUITING", "OTHER"], index=0)
    location = st.text_input("Location", value="Seattle")
    study_type = st.selectbox("Study Type", ["All", "Interventional", "Observational"], index=0)
    gender = st.selectbox("Gender", ["All", "Male", "Female"], index=0)
    age_group = st.selectbox("Age Group", ["Child (birth–17)", "Adult (18–64)", "Older Adult (65+)"], index=0)
    output_format = st.selectbox("Output Format", ["JSON", "CSV", "Excel"], index=1)

    if st.button("Search Clinical Trials"):
        term = ""  # Adjusted to not include age directly, as we now use age_group
        data = get_clinical_trials_data(condition, location, status, study_type, gender, age_group)

        if data:
            processed_data = process_all_studies(data)
            if processed_data:
                st.write(f"Found {len(processed_data)} studies matching the criteria.")

                # Displaying the processed data in Streamlit
                df = convert_to_dataframe(processed_data)
                st.dataframe(df)

                # Exporting data based on selected output format
                if output_format == "JSON":
                    json_data = df.to_json(orient="records")
                    st.download_button("Download JSON", json_data, "clinical_trials.json", "text/json", key='download-json')
                elif output_format == "CSV":
                    csv_data = df.to_csv(index=False)
                    st.download_button("Download CSV", csv_data, "clinical_trials.csv", "text/csv", key='download-csv')
                elif output_format == "Excel":
                    towrite = io.BytesIO()
                    df.to_excel(towrite, index=False, engine='openpyxl')  # Write to BytesIO buffer
                    towrite.seek(0)
                    st.download_button("Download Excel", towrite, "clinical_trials.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key='download-excel')

if __name__ == "__main__":
    main()