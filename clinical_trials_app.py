import requests
import pandas as pd
import json


def fetch_studies(condition, term, location, status, min_age, max_age, page_size=10):
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    
    # Advanced filter setup for age, if applicable
    age_filter = ""
    if min_age and max_age:
        age_filter = f"AREA[MinimumAge]RANGE[{min_age}, {max_age}]"
    
    params = {
        "format": "json",
        "query.cond": condition,
        "query.term": term,
        "query.locn": location,
        "filter.overallStatus": status,
        "filter.advanced": age_filter,
        "pageSize": page_size
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()  # Returns the JSON response from the API
    else:
        print(f"Error fetching studies: {response.status_code}")
        return None



def process_studies(data):
    processed_data = []
    for study in data['studies']:
        identification = study['protocolSection']['identificationModule']
        design = study['protocolSection'].get('designModule', {})
        eligibility = study['protocolSection'].get('eligibilityModule', {})
        contacts_locations = study['protocolSection'].get('contactsLocationsModule', {})
        central_contacts = contacts_locations.get('centralContacts', [])
        locations = contacts_locations.get('locations', [])
        phase = ', '.join(design.get('phases', ['Not Specified']))
        eligibility_criteria = eligibility.get('eligibilityCriteria', 'Not Specified')
        link_to_study = f"https://clinicaltrials.gov/ct2/show/{identification.get('nctId', 'N/A')}"
        primary_contact = central_contacts[0] if central_contacts else {}
        primary_location_info = locations[0] if locations else {}
        primary_location = primary_location_info.get('facility', 'Not Specified')
        primary_contact_info = f"Name: {primary_contact.get('name', 'N/A')}, " \
                               f"Role: {primary_contact.get('role', 'N/A')}, " \
                               f"Phone: {primary_contact.get('phone', 'N/A')}, " \
                               f"Email: {primary_contact.get('email', 'N/A')}"
        additional_locations_contacts = [f"Facility: {loc['facility']}, City: {loc.get('city', 'N/A')}, " \
                                         f"State: {loc.get('state', 'N/A')}, Country: {loc.get('country', 'N/A')}" \
                                         for loc in locations[1:]]
        processed_data.append([
            identification.get('briefTitle', 'N/A'),
            phase,
            eligibility_criteria,
            link_to_study,
            primary_location,
            primary_contact_info,
            " || ".join(additional_locations_contacts)
        ])
    return pd.DataFrame(processed_data, columns=['Title', 'Phase', 'Eligibility Criteria', 'Link to Study', 'Primary Location', 'Primary Contact', 'Additional Locations and Contacts'])

