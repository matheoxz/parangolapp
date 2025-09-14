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

    Serial.print("Left MPU - Accel: ");
    Serial.print(mpuDataL.ax); Serial.print(", ");
    Serial.print(mpuDataL.ay); Serial.print(", ");
    Serial.print(mpuDataL.az); Serial.print(" | Gyro: ");
    Serial.print(mpuDataL.gx); Serial.print(", ");
    Serial.print(mpuDataL.gy); Serial.print(", ");
    Serial.print(mpuDataL.gz); Serial.println();
    Serial.print("Right MPU - Accel: ");
    Serial.print(mpuDataR.ax); Serial.print(", ");
    Serial.print(mpuDataR.ay); Serial.print(", ");
    Serial.print(mpuDataR.az); Serial.print(" | Gyro: ");
    Serial.print(mpuDataR.gx); Serial.print(", ");
    Serial.print(mpuDataR.gy); Serial.print(", ");
    Serial.print(mpuDataR.gz); Serial.println();

    if (oscDiscoveryDone){
      sendOSCMessages(mpuDataL, mpuDataR);
    } else {
      playBassNote(mpuDataL);
      playMelodyNote(mpuDataR);
    }
  }
  
  delay(1000);
}