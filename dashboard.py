import streamlit as st
import pydeck as pdk
from gtfs_r import get_vehicle_positions
import time

st.title('PN Rapid Bus Real-time Tracker')

def create_map(data):
    if 'lat' in data.columns and 'lon' in data.columns:
        view_state = pdk.ViewState(
            latitude=data['lat'].mean(),
            longitude=data['lon'].mean(),
            zoom=11,
            pitch=0
        )
        
        layer = pdk.Layer(
            'ScatterplotLayer',
            data,
            get_position=['lon', 'lat'],
            get_radius=100,
            get_fill_color=[255, 0, 0, 140],
            pickable=True,
            opacity=0.8,
            stroked=True,
            filled=True
        )

        tooltip = {
            "html": "<b>Vehicle:</b> {vehicle.id}<br/>"
                   "<b>License:</b> {vehicle.licensePlate}<br/>"
                   "<b>Speed:</b> {position.speed} km/h",
            "style": {"backgroundColor": "steelblue", "color": "white"}
        }

        return pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip
        )
    return None

# Create two columns
col1, col2 = st.columns([2, 1])

# Auto-refresh data
if 'refresh' not in st.session_state:
    st.session_state.refresh = True

with col2:
    st.session_state.refresh = st.toggle('Auto-refresh', value=st.session_state.refresh)
    refresh_interval = st.slider('Refresh interval (seconds)', 10, 300, 30)

while True:
    # Get latest data
    df = get_vehicle_positions()
    
    with col1:
        st.subheader('Vehicle Locations')
        map_chart = create_map(df)
        if map_chart:
            st.pydeck_chart(map_chart)
        else:
            st.error('No location data available')
    
    with col2:
        st.subheader('Vehicle Information')
        st.write(f'Total Vehicles: {len(df)}')
        st.dataframe(df)
    
    if not st.session_state.refresh:
        break
        
    time.sleep(refresh_interval)
    st.rerun()
