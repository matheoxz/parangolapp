#include "mpu.h"

MPU6050 mpuL, mpuR;
bool allMpusInitialized = false;

void initMPU() {
    Serial.println("Initializing MPU devices...");
    Wire.begin();
    mpuL.initialize();
    mpuR.initialize();
    allMpusInitialized = mpuL.testConnection() && mpuR.testConnection();
    Serial.println("MPU devices initialized");
}

mpuData readMPU(MPU6050 &mpu) {
    int16_t ax, ay, az;
    int16_t gx, gy, gz;
    mpu.getAcceleration(&ax, &ay, &az);
    mpu.getRotation(&gx, &gy, &gz);

    mpuData data;
    data.ax = ax;
    data.ay = ay;
    data.az = az;
    data.gx = gx;
    data.gy = gy;
    data.gz = gz;
    data.temperature = mpu.getTemperature();

    return data;
}