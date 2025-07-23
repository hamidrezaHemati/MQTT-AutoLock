import paho.mqtt.client as mqtt
import time
from datetime import datetime
import os

# === Configuration ===
BROKER = "91.185.132.147"  # broker IP address
PORT = 1883                             

SUB_TOPIC = "test/truck/#"
PUB_TOPIC = "test/truck/0/command/lock"
CLIENT_ID = "dashboard_mqtt_hub" 

# === Callback: on connect ===
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker!")
        client.subscribe(SUB_TOPIC)
    else:
        print(f"❌ Failed to connect, return code {rc}")

# === Callback: on message ===
def on_message(client, userdata, msg):
    print(f"📥 Received on {msg.topic}: {msg.payload.decode()}")

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
