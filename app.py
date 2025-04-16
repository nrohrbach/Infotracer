import requests
import pandas as pd
import rasterio
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import geopandas as gpd

# Funktion zur Abfrage der Koordinaten (Beispiel)
# Funktion zur Abfrage der Koordinaten (Beispiel)
def get_coordinates(gemeinde):
    url = f"https://api3.geo.admin.ch/rest/services/api/SearchServer?searchText={gemeinde}&type=locations&sr=2056"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        lat = data['results'][0]['attrs'].get('lat')
        lon = data['results'][0]['attrs'].get('lon')
        x = data['results'][0]['attrs'].get('x')
        y = data['results'][0]['attrs'].get('y')
        return y, x, lat, lon
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return y, x, lat, lon
        
def create_map(center,dataframe):
    m = folium.Map(location=center,
        zoom_start=12,
        control_scale=True,
        tiles="https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/current/3857/{z}/{x}/{y}.jpeg",
        attr='Map data: &copy; <a href="https://www.swisstopo.ch" target="_blank" rel="noopener noreferrer">swisstopo</a>;<a href="https://www.bafu.admin.ch/" target="_blank" rel="noopener noreferrer">BAFU</a>'
    )
    
    # Punkt bei der center-Position hinzufügen
    folium.Marker(
        location=center,
        popup=gemeinde,
        icon=folium.Icon(color='red')
    ).add_to(m)
    
    # Add markers to the map
    for index, row in dataframe.iterrows():
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],  # Latitude, Longitude
            popup=f"Ort: {row['ort']}<br>Datum: {row['datum']}<br>Milieu: {row['milieu']}<br>Marker: {row['marker']}<br>Menge: {row['menge']}",
            tooltip=row['label'],
            icon=folium.Icon(color='blue')
            ).add_to(m)

    return m        
                
        

    
# Funktion welche Bounding Box um Punkt mit Radius berechnet
def calculate_map_extent(coordinates, radius):
    """Calculates the map extent for a given radius around coordinates.

    Args:
        coordinates: A list containing the longitude and latitude [longitude, latitude].
        radius: The radius in meters.

    Returns:
        A list representing the map extent [min_x, min_y, max_x, max_y] in LV95 coordinates,
        or None if an error occurs during coordinate transformation.
    """
    easting = coordinates[0]
    northing = coordinates[1]


    if coordinates:
        map_extent = [0, 0, 0, 0]
        map_extent[0] = easting - radius
        map_extent[1] = northing - radius
        map_extent[2] = easting + radius
        map_extent[3] = northing + radius

        url = "https://api3.geo.admin.ch/rest/services/all/MapServer/identify"
        params = {
            "geometry":  f"{map_extent[0]},{map_extent[1]},{map_extent[2]},{map_extent[3]}",  # Longitude, Latitude
            "geometryFormat": "geojson",
            "geometryType": "esriGeometryEnvelope",
            "sr": "2056",
            "lang": "de",
            "layers": "all:ch.bafu.hydrogeologie-markierversuche",
            "returnGeometry": "true",
            "tolerance": 0
        }
    
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes
    
            api_response = response.json()

            # Antworten des API als Dataframe speichern
            if api_response:
                results = []
                for feature in api_response['results']:
                    result = {
                        'lat': feature["properties"]['x'],
                        'lon': feature["properties"]['y'],
                        'ort': feature["properties"]['ort'],
                        'datum': feature["properties"]['datum'],
                        'milieu': feature["properties"]['milieu'],
                        'marker': feature["properties"]['markierstoff'],
                        'menge': feature["properties"]['menge_einheit'],
                        'label' : feature["properties"]['label']
                    }
                    results.append(result)
                else:
                    print("No results found.")
            # Create a Pandas DataFrame
            df = pd.DataFrame(results)
            
            # Create a Geodataframe
            dfgeo = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lat, df.lon),crs='EPSG:2056')
            
            # Convert the GeoDataFrame's CRS to WGS84 (latitude/longitude) for Folium
            dfgeo = dfgeo.to_crs(epsg=4326)
    
            
            return dfgeo
        except requests.exceptions.RequestException as e:
            return None


        





# App
# Streamlit app
st.title("Übersicht Markierversuche")
st.markdown(
    """
Im Rahmen von InfoTracer koordiniert, zentralisiert und archiviert das BAFU Informationen zu Markierversuchen im Grund- und Oberflächenwasser der Schweiz.

Welche Versuche wurden in Ihrer Nähe gemacht?

"""
)

# Suchfeld für die Eingabe der Gemeinde
gemeinde = st.text_input('Suchen Sie nach Gemeinde, Flurname oder Adresse:')

# Suchfeld für die Eingabe der Gemeinde

radius = st.number_input('Radius in m:')

# Hauptlogik
data = []
if gemeinde and radius:
    coordinatesOutput = get_coordinates(gemeinde)

    bbox = calculate_map_extent(coordinatesOutput[0:2],radius)

  
    # Zeige die Karte an
    st.session_state['m'] = create_map(coordinatesOutput[2:4],bbox)
    st_folium(st.session_state['m'], width=700)

    st.dataframe(bbox)
   

