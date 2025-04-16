import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_folium import folium_static
import folium
from folium.plugins import Fullscreen

st.set_page_config(layout="wide")

if "pages" not in st.session_state:
    st.session_state.pages = [1]
if "current" not in st.session_state:
    st.session_state.current = 1
if "data" not in st.session_state:
    st.session_state.data = {}
if "positions" not in st.session_state:
    st.session_state.positions = []

with st.sidebar:
    st.subheader("Input")
    name = st.text_input("Satellite Name", key=f"name_{st.session_state.current}")
    sat_id = st.number_input("Satellite ID", key=f"id_{st.session_state.current}")
    submit = st.button("Track")

    if submit:
        if not name or not sat_id:
            st.warning("Please fill out all fields")
        else:
            backend_response = {
                "TLE Data": "Line1, Line2, Line3",
                "Position": {
                    "longitude": 12.34 + len(st.session_state.positions),
                    "latitude": 56.78 + len(st.session_state.positions),
                    "altitude": 400.0 + len(st.session_state.positions),
                    "time": datetime.now().strftime("%Y-%m-%d | %H:%M:%S")
                }
            }

            st.session_state.data[st.session_state.current] = {
                "name": name,
                "id": sat_id,
                "TLE Data": backend_response["TLE Data"],
                "Position": backend_response["Position"]
            }

            st.session_state.positions.append(backend_response["Position"])

    st.divider()
    st.subheader("Information Collected")

    latest_data = st.session_state.data.get(st.session_state.current, {})
    latest_pos = latest_data.get("Position", {})

    st.write(f"**TLE Data:** {latest_data.get('TLE Data', '')}")
    st.write(f"**Longitude:** {latest_pos.get('longitude', '')}")
    st.write(f"**Latitude:** {latest_pos.get('latitude', '')}")
    st.write(f"**Altitude:** {latest_pos.get('altitude', '')}")
    st.write(f"**Time:** {latest_pos.get('time', '')}")

# --- Fullscreen Map Display ---
if len(st.session_state.positions) >= 1:
    df_map = pd.DataFrame(st.session_state.positions)
    latest = df_map.iloc[-1]

    # Create folium map
    folium_map = folium.Map(location=[latest["latitude"], latest["longitude"]], zoom_start=4)

    # Add fullscreen plugin
    Fullscreen(position='topright', title='Full Screen', title_cancel='Exit Full Screen', force_separate_button=True).add_to(folium_map)

    # Add markers
    for _, row in df_map.iterrows():
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=f"Lat: {row['latitude']}<br>Lon: {row['longitude']}<br>Alt: {row['altitude']}"
        ).add_to(folium_map)

    # Add path line
    if len(df_map) > 1:
        points = [[row["latitude"], row["longitude"]] for _, row in df_map.iterrows()]
        folium.PolyLine(points, color="blue", weight=2.5, opacity=1).add_to(folium_map)

    st.subheader("Satellite Position Map")
    folium_static(folium_map, width=1600, height=900)  # Maximize map area
else:
    st.info("No satellite positions to show on the map.")
