#include "osc_connector.h"

// Define UDP ports
WiFiUDP Udp;
String oscServerIp;
int oscServerPort1 = 8000;

bool oscDestinationConfigured = false;

OSCMessage accTop("/top/acc");
OSCMessage accBottom("/bottom/acc");

void setOscDestination(const char* ip, int port) {
    oscServerIp = ip;
    oscServerPort1 = port;
    oscDestinationConfigured = true;
    Serial.printf("OSC destination set to %s:%u\n", ip, port);
}

void sendOSCMessages(mmaData data, OSCMessage &msg) {
  // Publish accelerometer data
  msg.add((float)data.ax);
  msg.add((float)data.ay);
  msg.add((float)data.az);

  // Send to port
  Udp.beginPacket(oscServerIp.c_str(), oscServerPort1);
  msg.send(Udp);
  Udp.endPacket();
  msg.empty();
}