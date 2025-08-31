#pragma once

#include <ESPmDNS.h>         // mDNS for service discovery
#include <WiFiUdp.h>         // UDP for OSC
#include <OSCMessage.h>      // OSC messaging

#include "mma.h"

// Global OSC discovery and UDP packet variables
extern WiFiUDP Udp1;
extern String oscServerIp;
extern int oscServerPort1;

extern bool oscDiscoveryDone;

// OSC messages
extern OSCMessage accTop, accBottom;

// Discover OSC services on local network via mDNS
void discoverOSC();

void sendOSCMessages(mmaData data, OSCMessage &msg);