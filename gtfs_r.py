# pip install gtfs-realtime-bindings pandas requests
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict
import pandas as pd
from requests import get
import os
from utils import image_to_data_url
 
# Sample GTFS-R URL from Malaysia's Open API
URL = 'https://api.data.gov.my/gtfs-realtime/vehicle-position/prasarana?category=rapid-bus-kl'

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(CURRENT_DIR, "assets", "bus.png")

def get_vehicle_positions():
    # Parse the GTFS Realtime feed
    feed = gtfs_realtime_pb2.FeedMessage()
    response = get(URL)
    feed.ParseFromString(response.content)
    
    # Extract vehicle position information
    vehicle_positions = [MessageToDict(entity.vehicle) for entity in feed.entity]
    df = pd.json_normalize(vehicle_positions)
    
    # Prepare columns for map display
    if 'position.latitude' in df.columns and 'position.longitude' in df.columns:
        df['lat'] = df['position.latitude']
        df['lon'] = df['position.longitude']
        
        # Convert icon to data URL
        icon_data_url = image_to_data_url(ICON_PATH)
        
        # Add icon data with data URL
        df['icon_data'] = None
        df['icon_data'] = df.apply(lambda x: {
            "url": icon_data_url,
            "width": 64,
            "height": 64,
            "anchorY": 32,
            "anchorX": 32,
        }, axis=1)
        
        # Handle bearing/rotation
        if 'position.bearing' in df.columns:
            df['angle'] = df['position.bearing']
        else:
            df['angle'] = 0
    
    return df

if __name__ == "__main__":
    df = get_vehicle_positions()
    print(f'Total vehicles: {len(df)}')
    print(df)