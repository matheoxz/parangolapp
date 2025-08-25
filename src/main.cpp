#include "led_builtin_blinks.h"
#include "ble_gatt_connector.h"
#include "osc_connector.h"
#include "leds.h"
#include "mpu.h"
#include "buzzers.h"

mpuData mpuDataL, mpuDataR;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);

  // Initialize Serial, Wire and MPU
  Serial.begin(115200);

  initLed();
  initBLE();  // Initialize BLE for GATT server
  initMPU();  // Initialize MPU
}

void loop() {
  if (allMpusInitialized){
    mpuDataL = readMPU(mpuL);
    mpuDataR = readMPU(mpuR);
    playLed(mpuDataL, mpuDataR);

    if (oscDiscoveryDone){
      sendOSCMessages(mpuDataL, mpuDataR);
    } else {
      playBassNote(mpuDataL);
      playMelodyNote(mpuDataR);
    }
  }
  
  delay(1000);
}