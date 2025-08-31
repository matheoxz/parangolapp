#include "mma.h"

// Sensor instances (default I2C address 0x1C)
Adafruit_MMA8451 mmaTop = Adafruit_MMA8451();
Adafruit_MMA8451 mmaBottom = Adafruit_MMA8451();

bool allMmasInitialized = false;

// Initialize all MMA8451 sensors over I2C
void initMMA() {
    Serial.println("Initializing MMA8451 devices...");
    //Wire.begin();

    bool okTop = mmaTop.begin(0x1D);
    bool okBottom = mmaBottom.begin(0x1C);
    allMmasInitialized = okTop && okBottom;

    if (allMmasInitialized) {
        Serial.println("MMA8451 devices initialized");
        // Set measurement range
        mmaTop.setRange(MMA8451_RANGE_2_G);    // ±2 g: measures from –19.6 to +19.6 m/s² (highest resolution)
        mmaBottom.setRange(MMA8451_RANGE_8_G);// ±8 g: measures from –78.4 to +78.4 m/s² (captures larger forces)
    } else {
        if (!okTop)
        {
            Serial.println("Failed to initialize top MMA8451 device");
        }
        if (!okBottom)
        {
            Serial.println("Failed to initialize bottom MMA8451 device");
        }
    }
}

// Read acceleration data from specified MMA8451 sensor
mmaData readMMA(Adafruit_MMA8451 &mma) {
    mmaData data;
    sensors_event_t event;
    mma.getEvent(&event);
    data.ax = event.acceleration.x;
    data.ay = event.acceleration.y;
    data.az = event.acceleration.z;
    return data;
}