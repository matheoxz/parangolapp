#include "osc_connector.h"

// Define UDP ports
WiFiUDP Udp;
String oscServerIp;
int oscServerPort1 = 8000;

bool oscDiscoveryDone = false;

OSCMessage gyrL("left/gyr");
OSCMessage accL("left/acc");
OSCMessage gyrR("right/gyr");
OSCMessage accR("right/acc");

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

void sendOSCMessages(mpuData dataL, mpuData dataR) {
  // Publish accelerometer data
  accL.add((float)dataL.ax);
  accL.add((float)dataL.ay);
  accL.add((float)dataL.az);

  accR.add((float)dataR.ax);
  accR.add((float)dataR.ay);
  accR.add((float)dataR.az);    

  // Publish gyroscope data
  gyrL.add((float)dataL.gx);
  gyrL.add((float)dataL.gy);
  gyrL.add((float)dataL.gz);

  gyrR.add((float)dataR.gx);
  gyrR.add((float)dataR.gy);
  gyrR.add((float)dataR.gz);

  // Send to port
  Udp.beginPacket(oscServerIp.c_str(), oscServerPort1);
  accL.send(Udp);
  Udp.endPacket();
  accL.empty();

  Udp.beginPacket(oscServerIp.c_str(), oscServerPort1);
  accR.send(Udp);
  Udp.endPacket();
  accR.empty();

  Udp.beginPacket(oscServerIp.c_str(), oscServerPort1);
  gyrL.send(Udp);
  Udp.endPacket();
  gyrL.empty();

  Udp.beginPacket(oscServerIp.c_str(), oscServerPort1);
  gyrR.send(Udp);
  Udp.endPacket();
  gyrR.empty();
}