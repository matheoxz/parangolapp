#include "osc_connector.h"

// Define UDP ports
WiFiUDP Udp;
String oscServerIp;
int oscServerPort1 = 8000;

bool oscDiscoveryDone = false;

OSCMessage accTop("/top/acc");
OSCMessage accBottom("/bottom/acc");

// Discover OSC services on local network via mDNS
void discoverOSC() {
  if (!MDNS.begin("parangole")) {
    Serial.println("mDNS init failed");
    return;
  }

  Serial.println("mDNS responder started");
  int count = MDNS.queryService("osc", "udp");  // _osc._udp
  Serial.printf("%d OSC service(s) found\n", count);
  for (int i = 0; i < count; i++) {
    Serial.printf(" %d: %s %s:%u\n", i+1,
      MDNS.hostname(i).c_str(),
      MDNS.IP(i).toString().c_str(),
      MDNS.port(i)
    );

    // Store the first found service
    if (i == 0) {
      oscServerIp = MDNS.IP(i).toString();
      oscServerPort1 = MDNS.port(i);
      oscDiscoveryDone = true;
    }
  }
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