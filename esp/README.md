# Parangole ESP32

Configurable ESP32 firmware for reading sensors and sending acceleration and gyroscope data over OSC.

## Hardware

- ESP32 Dev Module (`esp32dev`)
- I2C sensors on the default `Wire` pins
- Default sensors: two MPU6050 devices
- Left sensor: address `0x68`
- Right sensor: address `0x69`

## Build and Upload

Open this directory in VS Code with PlatformIO.

```powershell
platformio run -e esp32dev
platformio run -e esp32dev --target upload --upload-port COM3
platformio device monitor --port COM3
```

Replace `COM3` with the board's serial port.

For the debug build:

```powershell
platformio run -e debug
platformio run -e debug --target upload --upload-port COM3
platformio device monitor --port COM3
```

The debug build prints the OSC destination and one line for every OSC path.

## Configuration

Edit `include/sensor_config.h`:

```cpp
#define DEVICE_NAME "PARANGOLE_SOM"

const std::vector<SensorConfiguration> SENSOR_CONFIGURATIONS = {
  {SensorModel::MPU6050, 0x68, "left"},
  {SensorModel::MPU6050, 0x69, "right"}
};
```

Available models:

- `SensorModel::MPU6050`: acceleration and gyroscope data.
- `SensorModel::MMA`: acceleration data using the ADXL345 implementation; gyro values are zero.

The sensor factory creates and initializes the configured sensors.

## BLE Setup

The device advertises with `DEVICE_NAME`.

Service UUID:

```text
eab05e32-bbf8-444c-b2a7-4311ed21d61d
```

Send WiFi credentials to `CRED_CHAR_UUID`:

```text
SSID;PASSWORD
```

`CRED_CHAR_UUID`:

```text
0663eb35-8ef2-4412-8981-326b53272d63
```

Send the OSC destination to `OSC_IP_CHAR_UUID`:

```text
192.168.1.50;8000
```

`OSC_IP_CHAR_UUID`:

```text
db031e80-0d15-45de-8c19-4f7bdce94800
```

Successful WiFi credentials and OSC destinations are saved with `Preferences` and restored after reboot.

## OSC Output

For a sensor configured with the label `left`, the firmware sends:

```text
/left/acc    ax, ay, az
/left/gyr    gx, gy, gz
```

The `right` sensor uses `/right/acc` and `/right/gyr`. Messages are sent by UDP to the configured OSC IP and port.

## Future Configuration

The current factory supports MPU6050 and MMA/ADXL345 sensors. Future work can add:

- Configurable I2C SDA/SCL and interrupt pins.
- More sensor models.
- BLE configuration for sensors and OSC paths.
- Custom OSC payloads and channel suffixes.

## Project Layout

- `include/sensor_config.h`: device name and sensor list.
- `include/sensor_factory.h`, `src/sensor_factory.cpp`: sensor interface and implementations.
- `src/main.cpp`: setup, sensor reads, and OSC loop.
- `src/ble_gatt_connector.cpp`: BLE and WiFi provisioning.
- `src/osc_conector.cpp`: OSC persistence and sending.
- `platformio.ini`: build environments and dependencies.
