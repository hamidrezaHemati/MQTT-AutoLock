import paho.mqtt.client as mqtt
import time
from datetime import datetime
import os
import csv
import json

# === Configuration ===
BROKER = "89.219.240.178"  # broker IP address
PORT = 1883                             

SUB_TOPIC = "test/truck/+/data"
PUB_TOPIC = "test/truck/0/command/lock"
CLIENT_ID = "dashboard_mqtt_hub" 

# Get absolute path to the folder this script is in
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "mqtt_messages.csv")
log_path = os.path.join(script_dir, "mqtt_messages.log")

# === Ensure CSV has a header row ===
if not os.path.exists(csv_path):
    with open(csv_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "topic", "module_id", "lat", "lon", "raw_payload"])

# === Callback  ===
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker!")
        client.subscribe(SUB_TOPIC)
    else:
        print(f"❌ Failed to connect, return code {rc}")

# === Callback ===
def on_message(client, userdata, msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    payload = msg.payload.decode()
    topic = msg.topic
    
    # Extract truck id from topic: expected format "test/truck/<truck_id>/..."
    topic_parts = topic.split('/')
    module_ID = topic_parts[2] if len(topic_parts) > 2 else None
    module_ID = str(module_ID)
    
    lat = lon = None

    log_line = f"{timestamp} | {msg.topic} | {module_ID} | {payload}"
    print(f"📥 {log_line}")

    # Append to log file
    with open(log_path, "a") as logfile:
        logfile.write(log_line + "\n")
    
    try:
        payload_dict = json.loads(payload)
        lat = payload_dict.get("lat")
        lon = payload_dict.get("lon")
    except json.JSONDecodeError:
        pass  # payload is not JSON (e.g., "lock" or "unlock")

    # Append to CSV
    with open(csv_path, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, topic, module_ID, lat, lon, payload])

# === Create client and set credentials ===
client = mqtt.Client(CLIENT_ID)


client.on_connect = on_connect
client.on_message = on_message

# === Connect and start loop ===
client.connect(BROKER, PORT, 60)
client.loop_start()

# === Example Publish ===
import time

try:
    while True:
        # message = "Hello from Python MQTT client"
        # client.publish(PUB_TOPIC, message)
        # print(f"📤 Published to {PUB_TOPIC}: {message}")
        time.sleep(5)

except KeyboardInterrupt:
    print("🛑 Disconnecting...")
    client.loop_stop()
    client.disconnect()
