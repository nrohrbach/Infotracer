import requests
import pandas as pd
import rasterio
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# Funktion zur Abfrage der Koordinaten (Beispiel)
# Funktion zur Abfrage der Koordinaten (Beispiel)
def get_coordinates(gemeinde):
    url = f"https://api3.geo.admin.ch/rest/services/api/SearchServer?searchText={gemeinde}&type=locations&sr=2056"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        x = data['results'][0]['attrs'].get('x')
        y = data['results'][0]['attrs'].get('y')
        lat = data['results'][0]['attrs'].get('lat')
        lon = data['results'][0]['attrs'].get('lon')
        return y, x, lat, lon
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return y, x, lat, lon



# App
# Streamlit app
st.title("Luftqualität in deiner Gemeinde")
st.markdown(
    """
Dank der erfolgreichen Schweizer Luftreinhaltepolitik hat sich die Luftqualität in der Schweiz seit den 1990er Jahren deutlich verbessert.

Wie sieht die Luftqualität in deiner Gemeinde aus? Finde es heraus:

"""
)

# Suchfeld für die Eingabe der Gemeinde
gemeinde = st.text_input('Gib den Namen der Gemeinde ein:')

# Hauptlogik
data = []
if gemeinde:
    coordinatesOutput = get_coordinates(gemeinde)
  
    # Zeige die Karte an
    st.session_state['m'] = create_map(coordinatesOutput[2:4],year) 
    st_folium(st.session_state['m'], width=700)
