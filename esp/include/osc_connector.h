#pragma once

#include <WiFiUdp.h>         // UDP for OSC
#include <OSCMessage.h>      // OSC messaging

#include "mma.h"

// Global OSC discovery and UDP packet variables
extern WiFiUDP Udp1;
extern String oscServerIp;
extern int oscServerPort1;

extern bool oscDiscoveryDone;
extern bool oscDestinationConfigured;

// Discover OSC services on local network via mDNS
void discoverOSC();

// Load the last saved OSC destination from non-volatile storage.
void initOSC();

void sendOSCMessages(const SensorData& data, const char* oscAddress);
void setOscDestination(const char* ip, int port);