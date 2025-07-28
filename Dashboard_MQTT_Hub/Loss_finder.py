import paho.mqtt.client as mqtt
import time
from datetime import datetime
import os
import csv
import json
import matplotlib.pyplot as plt

# === Configuration ===
BROKER = "89.219.240.178"
PORT = 1883
SUB_TOPIC = "test/module"
CLIENT_ID = "dashboard_mqtt_hub_loss"

start_data = 0
data = []
timestamps = []
time_diffs = []
isFirstData = True

# Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(script_dir, "mqtt_messages.log")

# === Callbacks ===
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker!")
        client.subscribe(SUB_TOPIC)
    else:
        print(f"❌ Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    global start_data, data, timestamps, time_diffs, isFirstData

    now = time.time()
    timestamps.append(now)

    try:
        payload = int(msg.payload.decode())
    except ValueError:
        print(f"[!] Received non-integer payload: {msg.payload}")
        return
    
    if isFirstData:
        isFirstData = False
        return

    if len(timestamps) >= 2:
        delta = timestamps[-1] - timestamps[-2]
        time_diffs.append(delta)
        avg_delta = sum(time_diffs) / len(time_diffs)
    else:
        delta = 0
        avg_delta = 0

    timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if start_data == 0:
        start_data = payload

    data.append(payload)

    expected_total = payload - start_data + 1
    received_total = len(data)
    missed = expected_total - received_total
    loss_percent = (missed / expected_total * 100.0) if expected_total > 0 else 0.0

    log_line = (
        f"{timestamp_str} | {msg.topic} | Payload: {payload} | "
        f"Loss: {loss_percent:.2f}% | Missed: {missed} | "
        f"Δt: {delta:.3f}s | Avg Δt: {avg_delta:.3f}s"
    )

    print("📥", log_line)
    with open(log_path, "a", encoding="utf-8") as logfile:
        logfile.write(log_line + "\n")

# === MQTT Client ===
client = mqtt.Client(CLIENT_ID)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("🛑 Disconnecting...")
    client.loop_stop()
    client.disconnect()

    # === Plotting ===
    if time_diffs:
        plt.figure(figsize=(12, 6))

        # Plot individual time differences
        plt.subplot(2, 1, 1)
        plt.plot(time_diffs, marker='o', label='Δt between messages')
        plt.ylabel("Seconds")
        plt.title("Time Difference Between Received MQTT Messages")
        plt.grid(True)
        plt.legend()

        # Plot moving average (optional)
        avg_diffs = [sum(time_diffs[:i+1]) / (i+1) for i in range(len(time_diffs))]
        plt.subplot(2, 1, 2)
        plt.plot(avg_diffs, color='orange', label='Average Δt over time')
        plt.ylabel("Avg Seconds")
        plt.xlabel("Message Index")
        plt.title("Average Time Difference Between Messages")
        plt.grid(True)
        plt.legend()

        plt.tight_layout()
        plt.show()
