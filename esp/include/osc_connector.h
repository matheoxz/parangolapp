#pragma once

#include <WiFiUdp.h>         // UDP for OSC
#include <OSCMessage.h>      // OSC messaging

#include "mpu.h"

// Global OSC discovery and UDP packet variables
extern WiFiUDP Udp1;
extern String oscServerIp;
extern int oscServerPort1;

extern bool oscDestinationConfigured;

// OSC messages
extern OSCMessage accR, accL;

void sendOSCMessages(mpuData data, OSCMessage &msg);
void setOscDestination(const char* ip, int port);