#pragma once

#include <Arduino.h>
#include <vector>

// Device identity and sensor wiring/configuration for this Parangole build.
#define DEVICE_NAME "PARANGOLE_SOM"

enum class SensorModel {
  MPU6050,
  MMA
};

struct SensorConfiguration {
  SensorModel model;
  uint8_t i2cAddress;
  const char* oscAddress;
};

extern const std::vector<SensorConfiguration> SENSOR_CONFIGURATIONS;