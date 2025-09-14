#include "led_builtin_blinks.h"
#include "ble_gatt_connector.h"
#include "osc_connector.h"
#include "leds.h"
#include "mma.h"

mmaData mmaDataTop, mmaDataBottom;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);

  // Initialize Serial, Wire and MMA
  Serial.begin(115200);

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

  initLeds();
  initBLE();  // Initialize BLE for GATT server
  initMMA();  // Initialize MMA8451 sensors
}

void loop() {
  if (allMmasInitialized) {
    mmaDataTop = readMMA(mmaTop);
    mmaDataBottom = readMMA(mmaBottom);
    playLeds(mmaDataTop, mmaDataBottom);

    if (oscDestinationConfigured){
      sendOSCMessages(mmaDataTop, accTop);
      sendOSCMessages(mmaDataBottom, accBottom);
    }

    //Serial.printf("Top Acc: X: %f, Y: %f, Z: %f\n", mmaDataTop.ax, mmaDataTop.ay, mmaDataTop.az);
    //Serial.printf("Bottom Acc: X: %f, Y: %f, Z: %f\n", mmaDataBottom.ax, mmaDataBottom.ay, mmaDataBottom.az);
  }
  
  delay(50);
}