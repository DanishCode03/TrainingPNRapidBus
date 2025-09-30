import streamlit as st
import pydeck as pdk
from gtfs_r import get_vehicle_positions
import time
import os

# Add custom styling
st.markdown("""
    <style>
        .title-container {
            background-color: #0e1117;
            padding: 1rem;
            margin-bottom: 5rem;
            border-radius: 5px;
            text-align: center;
        }
        .title-text {
            color: white;
            font-size: 16px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Title in styled container
st.markdown('<div class="title-container"><p class="title-text">Rapid Bus Real-time Tracker</p></div>', unsafe_allow_html=True)

# Create assets directory if it doesn't exist
os.makedirs('assets', exist_ok=True)

def create_map(data):
    if 'lat' in data.columns and 'lon' in data.columns:
        # Verify icon data
        if 'icon_data' not in data.columns:
            st.error("Icon data not found in vehicle data")
            return None

        # Add rotation based on vehicle bearing if available
        data['angle'] = 0  # default angle
        if 'position.bearing' in data.columns:
            data['angle'] = data['position.bearing']

        view_state = pdk.ViewState(
            latitude=data['lat'].mean(),
            longitude=data['lon'].mean(),
            zoom=12,
            pitch=0
        )
        
        layer = pdk.Layer(
            'IconLayer',
            data,
            get_position=['lon', 'lat'],
            get_icon='icon_data',
            get_size=3,
            get_angle='angle',
            pickable=True,
            size_scale=10,
            opacity=0.8,
            icon_allow_overlap=False
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
            tooltip=tooltip,
            map_style='road'
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
    if not st.session_state.refresh:
        break
        
    time.sleep(refresh_interval)
    st.rerun()
