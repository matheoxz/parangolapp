#include "led_builtin_blinks.h"
#include "ble_gatt_connector.h"
#include "osc_connector.h"
#include "leds.h"
#include "mma.h"
#include "sensor_config.h"
#include "sensor_factory.h"

SensorFactory sensorFactory;
std::vector<std::unique_ptr<Sensor>> sensors;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);

  // Initialize Serial, Wire and MMA
  Serial.begin(115200);
  initOSC();

  // Scan I2C bus for devices and print found addresses
  Serial.println("Scanning I2C bus for devices...");
  Wire.begin();
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("I2C device found at 0x");
      if (addr < 16) Serial.print("0");
      Serial.println(addr, HEX);
    }
  }

  sensors = sensorFactory.create(SENSOR_CONFIGURATIONS);
  initLeds();
  initBLE();  // Initialize BLE for GATT server
}

void loop() {
  if (sensors.size() >= 2) {
    std::vector<SensorData> readings;
    readings.reserve(sensors.size());
    for (const std::unique_ptr<Sensor>& sensor : sensors) {
      readings.push_back(sensor->read());
    }

    playLeds(readings[0], readings[1]);

    if (oscDestinationConfigured){
#ifdef PARANGOLA_DEBUG
      // ANSI escape codes clear and reposition most serial terminals.
      Serial.print("\033[2J\033[H");
      Serial.printf("Destination: %s\n", oscServerIp.c_str());
#endif
      for (size_t index = 0; index < sensors.size(); ++index) {
        sendOSCMessages(readings[index], sensors[index]->configuration().oscAddress);
      }
    }
  }
  
  delay(50);
}