#pragma once

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <WiFi.h>

#include "led_builtin_blinks.h"
#include "osc_connector.h"

// Custom BLE service and characteristic UUIDs and device name
#define SERVICE_UUID        "eab05e32-bbf8-444c-b2a7-4311ed21d61d"
#define CRED_CHAR_UUID      "0663eb35-8ef2-4412-8981-326b53272d63"
#define IP_CHAR_UUID        "12345678-1234-1234-1234-1234567890ad"
#define DEVICE_BLE_NAME     "PARANGOLE_1"

void initBLE();