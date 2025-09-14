#pragma once

#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
#include <functional>
#include "mma.h"

#define LED_LEN_1 42
#define LED_LEN_2 43
#define LED_LEN_3 42
#define LED_LEN_4 43
#define LED_LEN_5 42
#define LED_LEN_6 41
#define LED_LEN_7 42
#define LED_LEN_8 41

#define LED_PIN_1 32  // GPIO32
#define LED_PIN_2 33  // GPIO33
#define LED_PIN_3 25  // GPIO25
#define LED_PIN_4 26  // GPIO26
#define LED_PIN_5 27  // GPIO27
#define LED_PIN_6 14  // GPIO14
#define LED_PIN_7 12  // GPIO12
#define LED_PIN_8 13  // GPIO13

extern Adafruit_NeoPixel NeoPixel_1, NeoPixel_2, NeoPixel_3, NeoPixel_4,
                         NeoPixel_5, NeoPixel_6, NeoPixel_7, NeoPixel_8;

extern int pixel1, pixel2, pixel3, pixel4, pixel5, pixel6, pixel7, pixel8;


using StopCondition = std::function<bool()>;   // instead of bool(*)()


void initLeds();
void playLeds(mmaData dataTop, mmaData dataBottom);
void clearLeds();
void setPixelTrail(Adafruit_NeoPixel &strip, int pixel);
/// Set one pixel with its own brightness (0–255)
void setPixelColor(Adafruit_NeoPixel &strip,
                   uint16_t     idx,
                   uint8_t      r,
                   uint8_t      g,
                   uint8_t      b,
                   uint8_t      bri);
void walkingLeds(StopCondition shouldStop, uint16_t delayMs = 100);
void breathingLeds(StopCondition shouldPlay, uint16_t delayMs);
void energyLeds(StopCondition shouldPlay, uint16_t delayMs);
void rainingColors(StopCondition shouldPlay, uint16_t delayMs);