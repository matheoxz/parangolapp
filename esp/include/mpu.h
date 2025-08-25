#pragma once

#include <Wire.h>            // I2C functions
#include <MPU6050.h>         // Electronic Cats library

#define OUTPUT_READABLE_YAWPITCHROLL
#define OUTPUT_READABLE_REALACCEL
#define OUTPUT_TEAPOT

// Create an Electronic Cats MPU6050 object
extern MPU6050 mpuL, mpuR;

extern bool allMpusInitialized;

struct mpuData {
  float ax, ay, az;
  float gx, gy, gz;
  float temperature;
};

void initMPU();

mpuData readMPU(MPU6050 &mpu);