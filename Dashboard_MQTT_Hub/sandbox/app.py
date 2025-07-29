import os
import threading
from flask import Flask, render_template, jsonify, make_response, request
import paho.mqtt.client as mqtt
from datetime import datetime
from collections import deque

app = Flask(__name__, static_folder='static')

message_history = deque(maxlen=10)

CLIENT_ID = "dashboard_mqtt_hub"

# Globals for MQTT client and current config
client = None
current_config = {"ip": None, "port": None, "topic": None}

# global event and result container
connect_event = threading.Event()
connect_result = {"success": False, "msg": ""}

def on_connect(c, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker!")
        c.subscribe(current_config["topic"])
        connect_result["success"] = True
        connect_result["msg"] = "Connected successfully"
    else:
        print(f"❌ Failed to connect: {rc}")
        connect_result["success"] = False
        connect_result["msg"] = f"Failed to connect, return code {rc}"
    connect_event.set()

def on_message(c, userdata, msg):
    message_history.appendleft({
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "topic": msg.topic,
        "payload": msg.payload.decode()
    })
    print(f"📥 {message_history[0]['timestamp']} | {message_history[0]['topic']} | {message_history[0]['payload']}")


# def start_mqtt(ip, port, topic):
#     global client, current_config

#     if client:
#         try:
#             client.loop_stop()
#             client.disconnect()
#         except Exception as e:
#             print(f"❌ Error stopping old client: {e}")

#     client = mqtt.Client(CLIENT_ID)
#     client.on_connect = on_connect
#     client.on_message = on_message

#     current_config = {"ip": ip, "port": port, "topic": topic}

#     try:
#         client.connect(ip, int(port), 60)
#         client.loop_start()
#         print(f"🔄 Connecting to {ip}:{port} on topic '{topic}'")
#         return True, f"Connected to {ip}:{port} on topic '{topic}'"
#     except Exception as e:
#         print(f"❌ MQTT connection error: {e}")
#         return False, str(e)
    
def start_mqtt(ip, port, topic):
    global client, current_config, connect_event, connect_result

    if client:
        try:
            client.loop_stop()
            client.disconnect()
        except Exception as e:
            print(f"❌ Error stopping old client: {e}")

    client = mqtt.Client(CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message

    current_config = {"ip": ip, "port": port, "topic": topic}

    # Reset the event and connection result before connect attempt
    connect_event.clear()
    connect_result = {"success": False, "msg": ""}

    try:
        client.connect(ip, int(port), 60)
        client.loop_start()
    except Exception as e:
        print(f"❌ MQTT connection error: {e}")
        return False, f"Connection error: {e}"

    # Wait for on_connect callback (max 5 seconds)
    connected = connect_event.wait(timeout=5)

    if not connected:
        # Timeout waiting for connection
        return False, "Connection timed out"

    return connect_result["success"], connect_result["msg"]



@app.route('/')
def index():
    return render_template("index.html")


@app.route('/data')
def data():
    response = make_response(jsonify(list(message_history)))
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.route('/connect', methods=['POST'])
def connect():
    data = request.get_json()
    ip = data.get("ip")
    port = data.get("port")
    topic = data.get("topic")

    if not (ip and port and topic):
        return jsonify({"status": "error", "message": "IP, port, and topic are required"}), 400

    success, msg = start_mqtt(ip, port, topic)
    status = "connected" if success else "error"
    print("debug 1: ", status)
    print("debug2 : ", msg)
    return jsonify({"status": status, "message": msg})


if __name__ == "__main__":
    # No MQTT thread here because connection is initiated on-demand from web
    app.run(debug=True)
