#include "ble_gatt_connector.h"

BLECharacteristic *ipCharacteristic;

// Callback to handle BLE client connections for debugging
class ServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) override {
    Serial.println("BLE client connected");
    blinkGatt();
  }
  void onDisconnect(BLEServer* pServer) override {
    Serial.println("BLE client disconnected");
    blinkGatt();
  }
};

// Callback to handle credentials write and trigger WiFi connection
class CredCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic) override {
    std::string creds = pCharacteristic->getValue();
    // Expecting "SSID;PASSWORD"
    int sep = creds.find(';');
    String ssid = String(creds.substr(0, sep).c_str());
    String password = String(creds.substr(sep + 1).c_str());
    Serial.println("Received credentials:");
    Serial.print("  SSID: "); Serial.println(ssid);
    Serial.print("  Pass: "); Serial.println(password);

    // Connect to WiFi
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid.c_str(), password.c_str());
    Serial.print("Connecting to WiFi");
    int retries = 0;
    while (WiFi.status() != WL_CONNECTED && retries < 20) {
      blinkWifi();  // Blink LED to indicate connection attempt
      Serial.print('.');
      retries++;
    }
    String ipMsg;
    if (WiFi.status() == WL_CONNECTED) {
      ipMsg = WiFi.localIP().toString();
      Serial.println("\nWiFi connected: " + ipMsg);
      // Scan for OSC devices once WiFi is connected
      //discoverOSC();
    } else {
      ipMsg = "FAIL";
      Serial.println("\nWiFi connect failed");
    }

    // Notify IP address (or FAIL)
    ipCharacteristic->setValue(ipMsg.c_str());
    ipCharacteristic->notify();
    Serial.println("IP address sent over BLE");
  }
};

void initBLE() {
      // Initialize BLE
  BLEDevice::init(DEVICE_BLE_NAME);
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

  pService->start();
  // Start advertising
  BLEAdvertising *pAdvertising = pServer->getAdvertising();
  pAdvertising->start();
  Serial.println("BLE GATT server started, waiting for credentials...");
}