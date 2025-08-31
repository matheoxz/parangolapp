#pragma once

#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
#include "mma.h"

// total de leds aproximado
// cada led tem ~1,8cm 
#define LED_LEN 278

#define LED_PIN_MELODY 27 //D27
#define LED_LEN_MELODY 44

extern Adafruit_NeoPixel NeoPixel_B;
extern Adafruit_NeoPixel NeoPixel_M;

extern int pixelMelody, pixelBass;

void initLed();

void playLed(mmaData dataTop, mmaData dataCenter, mmaData dataBottom);