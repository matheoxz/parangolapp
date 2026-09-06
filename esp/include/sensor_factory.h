#pragma once

#include <Adafruit_ADXL345_U.h>
#include <Adafruit_MPU6050.h>
#include <memory>
#include <vector>

#include "sensor_config.h"

struct SensorData {
  float ax = 0.0f;
  float ay = 0.0f;
  float az = 0.0f;
  float gx = 0.0f;
  float gy = 0.0f;
  float gz = 0.0f;
};

class Sensor {
public:
  explicit Sensor(const SensorConfiguration& configuration)
      : configuration_(configuration) {}
  virtual ~Sensor() = default;

  virtual bool begin() = 0;
  virtual SensorData read() = 0;

  const SensorConfiguration& configuration() const { return configuration_; }
  bool isInitialized() const { return initialized_; }

protected:
  SensorConfiguration configuration_;
  bool initialized_ = false;
};

class SensorFactory {
public:
  std::vector<std::unique_ptr<Sensor>> create(
      const std::vector<SensorConfiguration>& configurations) const;
};