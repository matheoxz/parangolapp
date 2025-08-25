#pragma once

#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
#include "mpu.h"


#define LED_PIN_BASS 33 
#define LED_LEN_BASS 38

#define LED_PIN_MELODY 27 //D27
#define LED_LEN_MELODY 44

extern Adafruit_NeoPixel NeoPixel_B;
extern Adafruit_NeoPixel NeoPixel_M;

extern int pixelMelody, pixelBass;

void initLed();

void playLed(mpuData dataL, mpuData dataR);

void playBassLEDs();
void playMelodyLEDs();
void defineColorBass(float octave, float pitch, float duration);