#include "sensor_factory.h"

const std::vector<SensorConfiguration> SENSOR_CONFIGURATIONS = {
  {SensorModel::MPU6050, 0x68, "left"},
  {SensorModel::MPU6050, 0x69, "right"}
};

namespace {

class Mpu6050Sensor final : public Sensor {
public:
  explicit Mpu6050Sensor(const SensorConfiguration& configuration)
      : Sensor(configuration) {}

  bool begin() override {
    initialized_ = sensor_.begin(configuration_.i2cAddress);
    if (initialized_) {
      sensor_.setAccelerometerRange(MPU6050_RANGE_2_G);
      sensor_.setGyroRange(MPU6050_RANGE_250_DEG);
    }
    return initialized_;
  }

  SensorData read() override {
    SensorData data;
    sensors_event_t acceleration;
    sensors_event_t gyro;
    sensors_event_t temperature;
    sensor_.getEvent(&acceleration, &gyro, &temperature);
    data.ax = acceleration.acceleration.x;
    data.ay = acceleration.acceleration.y;
    data.az = acceleration.acceleration.z;
    data.gx = gyro.gyro.x;
    data.gy = gyro.gyro.y;
    data.gz = gyro.gyro.z;
    return data;
  }

private:
  Adafruit_MPU6050 sensor_;
};

class MmaSensor final : public Sensor {
public:
  explicit MmaSensor(const SensorConfiguration& configuration)
      : Sensor(configuration), sensor_(configuration.i2cAddress) {}

  bool begin() override {
    initialized_ = sensor_.begin();
    return initialized_;
  }

  SensorData read() override {
    SensorData data;
    sensors_event_t acceleration;
    sensor_.getEvent(&acceleration);
    data.ax = acceleration.acceleration.x;
    data.ay = acceleration.acceleration.y;
    data.az = acceleration.acceleration.z;
    return data;
  }

private:
  Adafruit_ADXL345_Unified sensor_;
};

}  // namespace

std::vector<std::unique_ptr<Sensor>> SensorFactory::create(
    const std::vector<SensorConfiguration>& configurations) const {
  std::vector<std::unique_ptr<Sensor>> sensors;
  sensors.reserve(configurations.size());

  for (const SensorConfiguration& configuration : configurations) {
    std::unique_ptr<Sensor> sensor;
    if (configuration.model == SensorModel::MPU6050) {
      sensor = std::unique_ptr<Sensor>(new Mpu6050Sensor(configuration));
    } else if (configuration.model == SensorModel::MMA) {
      sensor = std::unique_ptr<Sensor>(new MmaSensor(configuration));
    }

    if (sensor != nullptr) {
      sensor->begin();
      sensors.push_back(std::move(sensor));
    }
  }

  return sensors;
}