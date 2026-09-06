#include "ble_gatt_connector.h"
#include <Preferences.h>

BLECharacteristic *ipCharacteristic;
BLECharacteristic *oscIpCharacteristic;  // new: holds OSC destination writes

bool connectToWiFi(const String& ssid, const String& password) {
  if (ssid.length() == 0) {
    return false;
  }

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid.c_str(), password.c_str());
  Serial.print("Connecting to WiFi");
  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 20) {
    blinkWifi();
    Serial.print('.');
    retries++;
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("\nWiFi connect failed");
    return false;
  }

  Preferences preferences;
  preferences.begin("wifi", false);
  preferences.putString("ssid", ssid);
  preferences.putString("password", password);
  preferences.end();
  Serial.println("\nWiFi connected: " + WiFi.localIP().toString());
  return true;
}

void connectSavedWiFi() {
  Preferences preferences;
  preferences.begin("wifi", true);
  String ssid = preferences.getString("ssid", "");
  String password = preferences.getString("password", "");
  preferences.end();

  if (ssid.length() == 0) {
    Serial.println("No saved WiFi credentials");
    return;
  }

  Serial.println("Trying saved WiFi credentials for SSID: " + ssid);
  connectToWiFi(ssid, password);
}

// Callback to handle BLE client connections for debugging
class ServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) override {
    Serial.println("BLE client connected");
    blinkGatt();
  }
  void onDisconnect(BLEServer* pServer) override {
    Serial.println("BLE client disconnected");
    blinkGatt();

    BLEAdvertising *pAdvertising = pServer->getAdvertising();
    if (pAdvertising != nullptr) {
      pAdvertising->start();
      Serial.println("BLE advertising restarted for reconnection");
    }
  }
};

// Callback to handle credentials write and trigger WiFi connection
class CredCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic) override {
    std::string creds = pCharacteristic->getValue();
    // Expecting "SSID;PASSWORD"
    size_t sep = creds.find(';');
    if (sep == std::string::npos) {
      Serial.println("Invalid WiFi credentials format");
      return;
    }
    String ssid = String(creds.substr(0, sep).c_str());
    String password = String(creds.substr(sep + 1).c_str());
    Serial.println("Received credentials:");
    Serial.print("  SSID: "); Serial.println(ssid);

    // Connect to WiFi
    String ipMsg;
    if (connectToWiFi(ssid, password)) {
      ipMsg = WiFi.localIP().toString();
      // Scan for OSC devices once WiFi is connected
      //discoverOSC();
    } else {
      ipMsg = "FAIL";
    }

    // Notify IP address (or FAIL)
    String ipMsgFull = "IP:" + ipMsg;
    ipCharacteristic->setValue(ipMsgFull.c_str());
    ipCharacteristic->notify();
    Serial.println("IP address sent over BLE");
  }
};

class OscIpCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic) override {
    std::string val = pCharacteristic->getValue();            // "IP;PORT"
    size_t sep = val.find(';');
    if (sep == std::string::npos) {
      Serial.println("Invalid OSC destination format");
      return;
    }
    String oscIp   = String(val.substr(0, sep).c_str());
    int    oscPort = atoi(val.substr(sep + 1).c_str());
    if (oscIp.length() == 0 || oscPort <= 0 || oscPort > 65535) {
      Serial.println("Invalid OSC destination");
      return;
    }
    Serial.println("Received OSC IP and port:");
    Serial.print("  IP: ");   Serial.println(oscIp);
    Serial.print("  Port: "); Serial.println(oscPort);
    // new: tell your OSC connector where to send messages
    setOscDestination(oscIp.c_str(), oscPort);
  }
};

void initBLE() {
  connectSavedWiFi();

  // Initialize BLE
  BLEDevice::init(DEVICE_NAME);
  BLEServer *pServer = BLEDevice::createServer();
  pServer->setCallbacks(new ServerCallbacks());
  BLEService *pService = pServer->createService(SERVICE_UUID);

  // Credential characteristic (write only)
  BLECharacteristic *credCharacteristic = pService->createCharacteristic(
    CRED_CHAR_UUID,
    BLECharacteristic::PROPERTY_WRITE
  );
  credCharacteristic->setCallbacks(new CredCallbacks());

  // IP characteristic (notify only)
  ipCharacteristic = pService->createCharacteristic(
    IP_CHAR_UUID,
    BLECharacteristic::PROPERTY_NOTIFY
  );
  ipCharacteristic->addDescriptor(new BLE2902());

  // OSC IP characteristic (write only)
  oscIpCharacteristic = pService->createCharacteristic(
    OSC_IP_CHAR_UUID,
    BLECharacteristic::PROPERTY_WRITE
  );
  oscIpCharacteristic->setCallbacks(new OscIpCallbacks());

  pService->start();
  // Start advertising
  BLEAdvertising *pAdvertising = pServer->getAdvertising();
  pAdvertising->start();
  Serial.println("BLE GATT server started, waiting for credentials...");
}