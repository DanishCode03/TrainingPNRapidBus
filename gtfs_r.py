# pip install gtfs-realtime-bindings pandas requests
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict
import pandas as pd
from requests import get
 
# Sample GTFS-R URL from Malaysia's Open API
URL = 'https://api.data.gov.my/gtfs-realtime/vehicle-position/prasarana?category=rapid-bus-kl'

def get_vehicle_positions():
    # Parse the GTFS Realtime feed
    feed = gtfs_realtime_pb2.FeedMessage()
    response = get(URL)
    feed.ParseFromString(response.content)
    
    # Extract vehicle position information
    vehicle_positions = [MessageToDict(entity.vehicle) for entity in feed.entity]
    df = pd.json_normalize(vehicle_positions)
    
    # Rename columns for easier access
    if 'position.latitude' in df.columns and 'position.longitude' in df.columns:
        df['lat'] = df['position.latitude']
        df['lon'] = df['position.longitude']
    
    return df

if __name__ == "__main__":
    df = get_vehicle_positions()
    print(f'Total vehicles: {len(df)}')
    print(df)