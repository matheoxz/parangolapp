#pragma once
#include <Arduino.h>
#include <Wire.h>            // I2C functions
#include <Adafruit_Sensor.h>  // Sensor base class
#include <Adafruit_MMA8451.h> // MMA8451 accelerometer

// Sensor instances and initialization flag
extern Adafruit_MMA8451 mmaTop, mmaBottom;
extern bool allMmasInitialized;

struct mmaData {
  float ax, ay, az;
};

void initMMA();

mmaData readMMA(Adafruit_MMA8451 &mma);