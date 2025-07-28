from flask import Flask, render_template, request, jsonify
import paho.mqtt.client as mqtt

app = Flask(__name__, static_folder='styles')
mqtt_client = mqtt.Client()

@app.route("/")
def index():
    gps_data = [
        (35.76806173848087, 51.472052385284385),
        (35.776215087404076, 51.47687022102022),
        (35.78583656563752, 51.496075477693886),
        (35.77133987830734, 51.55277661222864),
        (35.74344126742332, 51.60691473941928),
        (35.7318862633797, 51.65330033204657),
        (35.75754248811002, 51.695968502049816),
        (35.74865194556357, 51.7390510916154),
        (35.74444296101705, 51.78625999255578),
        (35.733611261589814, 51.814824413343544),
        (35.72882044155193, 51.82530635818381),
    ]
    return render_template('index.html', gps_data=gps_data)

@app.route("/connect_mqtt", methods=["POST"])
def connect_mqtt():
    data = request.get_json()
    address = data["address"]
    port = int(data["port"])

    try:
        mqtt_client.connect(address, port, 60)
        mqtt_client.loop_start()
        return jsonify({"message": f"Connected to {address}:{port}"})
    except Exception as e:
        return jsonify({"message": f"Connection failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)

