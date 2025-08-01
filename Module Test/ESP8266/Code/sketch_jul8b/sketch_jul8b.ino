// 🔴 Board Select: NodeMCU 1.0 (ESP-12E Module)

#include <ESP8266WiFi.h>
#include <Servo.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// === GPIO Pins ===
const int wifi_connect = 4;   // D2
const int wifi_disconnect = 12; // D6
const int mqtt_pub = 2;       // D4
const int mqtt_sub = 14;      // D5

// === Wi-Fi Credentials ===
//const char* ssid = "AvaPardaz";
//const char* password = "00148615501371";

const char* ssid = "Galaxy A30sD1CD";
const char* password = "dtjp9767";

// === MQTT Settings ===
const char* mqtt_server = "89.219.240.178";
const int mqtt_port = 1883;
int ID = 0; // or "1" for the second board
String clientId = "ESP8266Client-" + String(ID); // ID should be 1 or 2
//String mqtt_sub_topic = "test/truck/" + String(ID) + "/command/lock";
//String mqtt_pub_topic = "test/truck/" + String(ID) + "/data";

String mqtt_sub_topic = "test/truck/" + String(ID) + "/command/lock";
String mqtt_pub_topic = "test/web";

WiFiClient espClient;
PubSubClient client(espClient);
Servo lock;

// === GPS Waypoints ===
struct Waypoint {
  float lat;
  float lon;
};

Waypoint gpsWaypoints[] = {
  {35.76806173848087, 51.472052385284385},
  {35.776215087404076, 51.47687022102022},
  {35.78583656563752,  51.496075477693886},
  {35.77133987830734,  51.55277661222864},
  {35.74344126742332,  51.60691473941928},
  {35.7318862633797,   51.65330033204657},
  {35.75754248811002,  51.695968502049816},
  {35.74865194556357,  51.7390510916154},
  {35.74444296101705,  51.78625999255578},
  {35.733611261589814, 51.814824413343544},
  {35.72882044155193,  51.82530635818381}
};
const int totalWaypoints = sizeof(gpsWaypoints) / sizeof(gpsWaypoints[0]);

unsigned long lastPublishTime = 0;
int currentWaypointIndex = 0;

// === Pin Assignments ===
const int locked_greenLedPin = D8;  // Green LED for LOCK
const int unlocked_redLedPin = D7;    // Red LED for UNLOCK

// === Status Variables ===
String lock_status = "unlock";  // Initial state


String* scan_available_networks(int& count) {
  Serial.println("Scanning for available WiFi networks...");

  count = WiFi.scanNetworks();
  Serial.println("Scan complete");

  if (count <= 0) {
    Serial.println("No networks found");
    return nullptr;
  }

  String* ssidList = new String[count];

  for (int i = 0; i < count; ++i) {
    ssidList[i] = WiFi.SSID(i);

    Serial.print(i + 1);
    Serial.print(": ");
    Serial.print(ssidList[i]);
    Serial.print(" RSSI: (");
    Serial.print(WiFi.RSSI(i));
    Serial.print(") MAC:");
    Serial.print(WiFi.BSSIDstr(i));
    Serial.println((WiFi.encryptionType(i) == ENC_TYPE_NONE) ? " Unsecured" : " Secured");
    delay(10);
  }

  Serial.println();
  return ssidList;
}

void connect_to_wifi(){
  //  Try connecting to WiFi
  Serial.printf("\nConnecting to %s\n", ssid);
  WiFi.begin(ssid, password);

  int maxAttempts = 20;
  while (WiFi.status() != WL_CONNECTED && maxAttempts-- > 0) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    // 🌐 Test internet access
    WiFiClient client;
    const char* host = "google.com"; // You can also try "google.com"

    Serial.print("Connecting to ");
    Serial.println(host);

    if (client.connect(host, 80)) {
      Serial.println("Internet access OK! 🟢");
      digitalWrite(wifi_connect, HIGH);
      digitalWrite(wifi_disconnect, LOW);
      client.stop();
    } else {
      Serial.println("Cannot reach host. Internet access might be down. 🔴");
      digitalWrite(wifi_connect, LOW);
      digitalWrite(wifi_disconnect, HIGH);
    }

  } else {
    Serial.println("\nFailed to connect to WiFi");
  }
}

bool isSSIDAvailable(const char* ssid, String* networks, int networkCount) {
  for (int i = 0; i < networkCount; ++i) {
    if (String(ssid) == networks[i]) {
      Serial.printf("Found '%s' in the available networks\n", ssid);
      return true;
    }
  }

  Serial.printf("'%s' is not available\n", ssid);
  return false;
}

// === MQTT Callback ===
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.println(topic);

  String message;
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  Serial.print("Payload: ");
  Serial.println(message);

  // Flash mqtt_sub LED
  digitalWrite(mqtt_sub, HIGH);
  delay(500);
  digitalWrite(mqtt_sub, LOW);

  // Optional: control servo with message
  if (message == "lock") {
    digitalWrite(mqtt_sub, HIGH);
    lock_status = "lock";
    lock.write(0);
    delay(500);
  } else if (message == "unlock") {
    digitalWrite(mqtt_sub, HIGH);
    lock_status = "unlock";
    lock.write(90);
    delay(500);
  }
  digitalWrite(mqtt_sub, LOW);
}

// === MQTT Connection ===
void connect_to_MQTT() {
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  while (!client.connected()) {
    Serial.print("Connecting to MQTT broker...");
    if (client.connect(clientId.c_str())) {
      Serial.println("connected!");
//      client.subscribe(mqtt_sub_topic);
      client.subscribe(mqtt_sub_topic.c_str());
      Serial.printf("Subscribed to: %s\n", mqtt_sub_topic);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds");
      delay(5000);
    }
  }
}


void setup() {
  Serial.begin(115200);
  delay(100);

  pinMode(wifi_connect, OUTPUT);
  pinMode(wifi_disconnect, OUTPUT);
  pinMode(mqtt_pub, OUTPUT);
  pinMode(mqtt_sub, OUTPUT);
  pinMode(locked_greenLedPin, OUTPUT);
  pinMode(unlocked_redLedPin, OUTPUT);

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();  // Start fresh
  delay(100);


  int networkCount = WiFi.scanNetworks();

  digitalWrite(wifi_connect, HIGH);
  digitalWrite(wifi_disconnect, HIGH);
  digitalWrite(mqtt_pub, HIGH);
  digitalWrite(mqtt_sub, HIGH);
  delay(2000);

  String* networks = scan_available_networks(networkCount);

  digitalWrite(wifi_connect, LOW);
  digitalWrite(wifi_disconnect, LOW);
  digitalWrite(mqtt_pub, LOW);
  digitalWrite(mqtt_sub, LOW);

  if (isSSIDAvailable(ssid, networks, networkCount)) {
    connect_to_wifi();
  } else {
    digitalWrite(wifi_connect, LOW);
    digitalWrite(wifi_disconnect, HIGH);
    Serial.printf("Could not connect, The '%s' network does not exists in the available networks\n", ssid);
    Serial.println("Please check the SSID or move closer to the access point.");
  }
  
  lock.attach(5);  // attaches the servo on GIO5 D1 to the servo object
  lock.write(0);
  delay(1000); 


}

void loop() {
  // Reconnect WiFi if needed
  if (WiFi.status() != WL_CONNECTED) {
    digitalWrite(wifi_connect, LOW);
    digitalWrite(wifi_disconnect, HIGH);
    Serial.println("WiFi lost! Reconnecting...");
    connect_to_wifi();
    return;
  }

  // Maintain MQTT connection
  if (!client.connected()) {
    connect_to_MQTT();
  }

  client.loop();

  // Publish GPS data every 10 seconds
  if (millis() - lastPublishTime >= 10000 && client.connected()) {
    if (currentWaypointIndex < totalWaypoints) {
      StaticJsonDocument<128> doc;
      doc["lat"] = gpsWaypoints[currentWaypointIndex].lat;
      doc["lon"] = gpsWaypoints[currentWaypointIndex].lon;

      char payload[128];
      serializeJson(doc, payload);

      client.publish(mqtt_pub_topic.c_str(), payload);

      Serial.print("Published waypoint ");
      Serial.print(currentWaypointIndex + 1);
      Serial.print(": ");
      Serial.println(payload);

      digitalWrite(mqtt_pub, HIGH);
      delay(100);
      digitalWrite(mqtt_pub, LOW);

      currentWaypointIndex++;
      lastPublishTime = millis();
      if (currentWaypointIndex >= totalWaypoints){
        currentWaypointIndex = 0;
      }
    }
  }
  
  // Control LEDs based on lock_status
  if (lock_status == "lock") {
    digitalWrite(locked_greenLedPin, HIGH);  // Green ON
    digitalWrite(unlocked_redLedPin, LOW);     // Red OFF
  } else if (lock_status == "unlock") {
    digitalWrite(locked_greenLedPin, LOW);   // Green OFF
    digitalWrite(unlocked_redLedPin, HIGH);    // Red ON
  }

}
