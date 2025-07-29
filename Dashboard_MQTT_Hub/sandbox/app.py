import os
import threading
import time
from flask import Flask, render_template, jsonify, make_response
import paho.mqtt.client as mqtt
from datetime import datetime

app = Flask(__name__)
latest_data = {"timestamp": None, "topic": None, "payload": None}

BROKER = "89.219.240.178"
PORT = 1883
SUB_TOPIC = "test/web"
CLIENT_ID = "dashboard_mqtt_hub"

# === MQTT Setup ===
client = mqtt.Client(CLIENT_ID)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker!")
        client.subscribe(SUB_TOPIC)
    else:
        print(f"❌ Failed to connect: {rc}")

def on_message(client, userdata, msg):
    global latest_data
    latest_data = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "topic": msg.topic,
        "payload": msg.payload.decode()
    }
    print(f"📥 {latest_data['timestamp']} | {latest_data['topic']} | {latest_data['payload']}")

def mqtt_loop():
    try:
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(BROKER, PORT, 60)
        client.loop_forever()
    except Exception as e:
        print(f"❌ MQTT loop error: {e}")

# === Flask Routes ===
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/data')
def data():
    response = make_response(jsonify(latest_data))
    response.headers['Cache-Control'] = 'no-store'
    return response

# === Main Entry Point ===
if __name__ == "__main__":
    # Run MQTT only in actual reloader process
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Thread(target=mqtt_loop, daemon=True).start()

    app.run(debug=True)
