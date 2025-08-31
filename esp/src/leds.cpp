#include "leds.h"

Adafruit_NeoPixel NeoPixel_M(LED_LEN_MELODY, LED_PIN_MELODY, NEO_GRB + NEO_KHZ800);

void initLed() {
  NeoPixel_M.begin();
  NeoPixel_M.show();
}

void playLed(mmaData dataTop, mmaData dataCenter, mmaData dataBottom) {
  // implement
}