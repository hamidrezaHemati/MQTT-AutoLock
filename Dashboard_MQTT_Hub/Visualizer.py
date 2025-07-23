import pandas as pd
import folium
import time
import os

MODULE_ID = "1"

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "mqtt_messages.csv")
MAP_FILE = os.path.join(script_dir, "truck1_map.html")

def create_map(lat, lon):
    fmap = folium.Map(location=[lat, lon], zoom_start=15)
    folium.Marker([lat, lon], tooltip=f"Truck {MODULE_ID}").add_to(fmap)

    # Save to HTML
    fmap.save(MAP_FILE)

    # Inject auto-refresh JavaScript
    with open(MAP_FILE, "r+", encoding="utf-8") as f:
        html = f.read()
        refresh_script = """
        <script>
            setTimeout(function(){
                window.location.reload(1);
            }, 5000); // reload every 5 seconds
        </script>
        """
        if refresh_script not in html:
            html = html.replace("</body>", refresh_script + "\n</body>")
            f.seek(0)
            f.write(html)
            f.truncate()
    
    print(f"Map updated at lat={lat}, lon={lon}")

def read_latest_location():
    if not os.path.exists(csv_path):
        print("CSV file not found:", csv_path)
        return None, None
    
    df = pd.read_csv(csv_path)
    # Filter rows where module_id == MODULE_ID and lat/lon not null
    truck_data = df[(df['module_id'].astype(str) == MODULE_ID) & df['lat'].notnull() & df['lon'].notnull()]
    print(df.dtypes)
    print(df['module_id'].unique())
    print(truck_data)
    
    if truck_data.empty:
        print(f"No location data for truck {MODULE_ID} yet.")
        return None, None
    
    # Get latest row by timestamp (assuming timestamp column exists and sorted)
    latest = truck_data.iloc[-1]
    return float(latest['lat']), float(latest['lon'])

def main():
    print("Starting real-time map for truck", MODULE_ID)
    last_location = (None, None)

    try:
        while True:
            lat, lon = read_latest_location()
            if lat is not None and lon is not None:
                if (lat, lon) != last_location:
                    create_map(lat, lon)
                    last_location = (lat, lon)
            time.sleep(5)  # check every 5 seconds
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()
