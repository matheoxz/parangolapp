#pragma once

#include <ESPmDNS.h>         // mDNS for service discovery
#include <WiFiUdp.h>         // UDP for OSC
#include <OSCMessage.h>      // OSC messaging

#include "mpu.h"

// Global OSC discovery and UDP packet variables
extern WiFiUDP Udp1;
extern String oscServerIp;
extern int oscServerPort1;

extern bool oscDiscoveryDone;

// OSC messages
extern OSCMessage gyrL, accL, gyrR, accR;

// Discover OSC services on local network via mDNS
void discoverOSC();

void sendOSCMessages(mpuData dataL, mpuData dataR);