#include "osc_connector.h"
#include <Preferences.h>

// Define UDP ports
WiFiUDP Udp;
String oscServerIp;
int oscServerPort1 = 8000;

bool oscDestinationConfigured = false;

void initOSC() {
  Preferences preferences;
  preferences.begin("osc", true);
  String savedIp = preferences.getString("ip", "");
  int savedPort = preferences.getInt("port", 0);
  preferences.end();

  if (savedIp.length() > 0 && savedPort > 0 && savedPort <= 65535) {
    setOscDestination(savedIp.c_str(), savedPort);
    Serial.printf("Loaded OSC destination: %s:%d\n", savedIp.c_str(), savedPort);
  }
}

void setOscDestination(const char* ip, int port) {
  oscServerIp = ip;
  oscServerPort1 = port;
  oscDestinationConfigured = true;
  Preferences preferences;
  preferences.begin("osc", false);
  preferences.putString("ip", ip);
  preferences.putInt("port", port);
  preferences.end();
  Serial.printf("OSC destination set to %s:%u\n", ip, port);
}

void sendOSCMessage(const SensorData& data, const String& path,
                    float x, float y, float z) {
  OSCMessage message(path.c_str());
  message.add(x);
  message.add(y);
  message.add(z);

  Udp.beginPacket(oscServerIp.c_str(), oscServerPort1);
  message.send(Udp);
  Udp.endPacket();
  message.empty();
}

void sendOSCMessages(const SensorData& data, const char* oscAddress) {
  String accelerationPath = String("/") + oscAddress + "/acc";
  String gyroPath = String("/") + oscAddress + "/gyr";

#ifdef PARANGOLA_DEBUG
  Serial.printf("%s\t%.3f\t%.3f\t%.3f\n",
                accelerationPath.c_str(),
                data.ax,
                data.ay,
                data.az);
  Serial.printf("%s\t%.3f\t%.3f\t%.3f\n",
                gyroPath.c_str(),
                data.gx,
                data.gy,
                data.gz);
#endif

  sendOSCMessage(data, accelerationPath, data.ax, data.ay, data.az);
  sendOSCMessage(data, gyroPath, data.gx, data.gy, data.gz);
}