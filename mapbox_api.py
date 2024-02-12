import requests
import streamlit as st  
MAPBOX_TOKEN = st.secrets["MAPBOX_TOKEN"]


def get_location_suggestions(query):
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json"
    params = {
        'access_token': MAPBOX_TOKEN,
        'autocomplete': True,
        'country': 'US'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        places = [feature['place_name'] for feature in data['features']]
        return places
    else:
        print(f"Error fetching location suggestions: {response.status_code}")
        return []