#include "leds.h"

Adafruit_NeoPixel NeoPixel_1(LED_LEN_1, LED_PIN_1, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel NeoPixel_2(LED_LEN_2, LED_PIN_2, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel NeoPixel_3(LED_LEN_3, LED_PIN_3, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel NeoPixel_4(LED_LEN_4, LED_PIN_4, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel NeoPixel_5(LED_LEN_5, LED_PIN_5, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel NeoPixel_6(LED_LEN_6, LED_PIN_6, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel NeoPixel_7(LED_LEN_7, LED_PIN_7, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel NeoPixel_8(LED_LEN_8, LED_PIN_8, NEO_GRB + NEO_KHZ800);

int pixel1 = 0, pixel2 = 0, pixel3 = 0, pixel4 = 0,
    pixel5 = 0, pixel6 = 0, pixel7 = 0, pixel8 = 0;

int energyBottom = 0, energyTop = 0;

int test = false;

void initLeds() {
  NeoPixel_1.begin();
  NeoPixel_1.show();
  //NeoPixel_2.begin();
  //NeoPixel_2.show();
  // NeoPixel_3.begin();
  // NeoPixel_3.show();
  // NeoPixel_4.begin();
  // NeoPixel_4.show();
  // NeoPixel_5.begin();
  // NeoPixel_5.show();
  // NeoPixel_6.begin();
  // NeoPixel_6.show();
  // NeoPixel_7.begin();
  // NeoPixel_7.show();
  // NeoPixel_8.begin();
  // NeoPixel_8.show();
}

void playLeds(mmaData dataTop, mmaData dataBottom) {
  if (!test) {
    //testLeds();
    test = true;
  }

  energyBottom = sqrt(pow(dataBottom.ax, 2) + pow(dataBottom.ay, 2) + pow(dataBottom.az, 2)) - 9.81;
  energyTop = sqrt(pow(dataTop.ax, 2) + pow(dataTop.ay, 2) + pow(dataTop.az, 2)) - 9.81;

  float delayMs = energyBottom == 0 ? 100 : 100 / energyBottom;

  rainingColors([]() { return (int(energyBottom) == 0 && int(energyTop) == 0); }, 50);

  breathingLeds([]() { return (int(energyBottom) != 0); }, delayMs);

}

void clearLeds() {
  NeoPixel_1.clear();
  NeoPixel_1.show();
  // NeoPixel_2.clear();
  // NeoPixel_2.show();
  // NeoPixel_3.clear();
  // NeoPixel_3.show();
  // NeoPixel_4.clear();
  // NeoPixel_4.show();
  // NeoPixel_5.clear();
  // NeoPixel_5.show();
  // NeoPixel_6.clear();
  // NeoPixel_6.show();
  // NeoPixel_7.clear();
  // NeoPixel_7.show();
  // NeoPixel_8.clear();
  // NeoPixel_8.show();
}

void walkingLeds(StopCondition shouldPlay, uint16_t delayMs) {
    // these statics preserve state between calls
  static unsigned long lastUpdate = 0;
  static bool          started    = false;

  clearLeds();

  // (re)initialize when we first start playing
  if (!started && shouldPlay()) {
    pixel1 = pixel2 = pixel3 = pixel4 =
    pixel5 = pixel6 = pixel7 = pixel8 = 0;
    lastUpdate = millis();
    started = true;
    Serial.println("Started walkingLeds");
  }

  if (started) {
    unsigned long now = millis();
    if (shouldPlay() && (now - lastUpdate >= delayMs)) {
      lastUpdate = now;
      setPixelTrail(NeoPixel_1, pixel1);
      pixel1 = (pixel1 + 1) % NeoPixel_1.numPixels();
      // setPixelColor(NeoPixel_2, pixel2, 0, 150, 0); 
      // pixel2 = (pixel2 + 1) % NeoPixel_2.numPixels(); 
      // setPixelColor(NeoPixel_3, pixel3, 0, 150, 0);
      // pixel3 = (pixel3 + 1) % NeoPixel_3.numPixels();
      // setPixelColor(NeoPixel_4, pixel4, 0, 150, 0);
      // pixel4 = (pixel4 + 1) % NeoPixel_4.numPixels();
      // setPixelColor(NeoPixel_5, pixel5, 0, 150, 0);
      // pixel5 = (pixel5 + 1) % NeoPixel_5.numPixels();
      // setPixelColor(NeoPixel_6, pixel6, 0, 150, 0);
      // pixel6 = (pixel6 + 1) % NeoPixel_6.numPixels();
      // setPixelColor(NeoPixel_7, pixel7, 0, 150, 0);
      // pixel7 = (pixel7 + 1) % NeoPixel_7.numPixels();
      // setPixelColor(NeoPixel_8, pixel8, 0, 150, 0);
      // pixel8 = (pixel8 + 1) % NeoPixel_8.numPixels();
    }
    // stop and reset if condition no longer holds
    if (!shouldPlay()) {
      started = false;
    }
  }
}

void rainingColors(StopCondition shouldPlay, uint16_t delayMs) {
  static unsigned long lastUpdate   = 0;
  static bool          started      = false;
  static int           currentPixel = 0;
  static uint8_t       r, g, b;

  if (!started && shouldPlay()) {
    // start up
    lastUpdate   = millis();
    currentPixel = 0;
    // pick one random color for this “rain”
    r = random(0, 256);
    g = random(0, 256);
    b = random(0, 256);
    //clearLeds();       // start from blank
    started = true;
  }

  if (started) {
    unsigned long now = millis();
    if (shouldPlay() && (now - lastUpdate >= delayMs)) {
      lastUpdate = now;
      // light the next pixel
      NeoPixel_1.setPixelColor(currentPixel, NeoPixel_1.Color(r, g, b));
      NeoPixel_1.show();
      currentPixel++;
      // if we filled all pixels, end
      if (currentPixel >= NeoPixel_1.numPixels()) {
        started = false;
      }
    }
    // if condition disappeared mid-rain, bail out
    if (!shouldPlay()) {
      started = false;
    }
  }
}

void energyLeds(StopCondition shouldPlay, uint16_t delayMs) {
  static unsigned long lastUpdate = 0;
  static bool          started    = false;

  if (!started && shouldPlay()) {
    lastUpdate = millis();
    started = true;
    clearLeds();
  }

  int mappedEnergyToLed = map(energyBottom, 0, 40, 0, 41);
  mappedEnergyToLed = constrain(mappedEnergyToLed, 0, 41);

  if (started) {
    unsigned long now = millis();
    if (shouldPlay() && (now - lastUpdate >= delayMs)) {
      lastUpdate = now;
      //clearLeds();
      int randomOffset = random(0, 10);
      Serial.print("Filling up to ");
      Serial.println(mappedEnergyToLed - randomOffset);
      for (int i = 0; i < mappedEnergyToLed - randomOffset; i++)
      {
        NeoPixel_1.setPixelColor(i, NeoPixel_1.Color(random(0, 100), random(100, 255), random(50, 150)));
        NeoPixel_1.show();
      }
    }

    if (!shouldPlay()) {
      started = false;
    }
  }
}

void setPixelTrail(Adafruit_NeoPixel &strip, int pixel) {
  int mappedPixel = map(pixel, 0, strip.numPixels(), 0, 255);
  float r = random(); 
  float g = random();
  float b = random();
  setPixelColor(strip, (pixel - 2 + strip.numPixels()) % strip.numPixels(), (mappedPixel * r), (mappedPixel * g), (mappedPixel * b), 64);
  setPixelColor(strip, (pixel - 1 + strip.numPixels()) % strip.numPixels(), (mappedPixel * r), (mappedPixel * g), (mappedPixel * b), 128);
  setPixelColor(strip, pixel, mappedPixel * r, mappedPixel * g, mappedPixel * b, 255);
  setPixelColor(strip, (pixel + 1) % strip.numPixels(), (mappedPixel * r), (mappedPixel * g), (mappedPixel * b), 128);
  setPixelColor(strip, (pixel + 2) % strip.numPixels(), (mappedPixel * r), (mappedPixel * g), (mappedPixel * b), 64);
  strip.show();
}

void breathingLeds(StopCondition shouldPlay, uint16_t delayMs) {
  static unsigned long lastUpdate = 0;
  static bool          started    = false;
  // now hold a floating‐point brightness for smooth ln() math
  static float         brightness = 0.0f;
  // direction: +1 = ramp up, -1 = ramp down
  static int           direction  = 1;

  if (!started && shouldPlay()) {
    lastUpdate  = millis();
    brightness  = 0.0f;
    direction   = 1;
    started     = true;
  }

  if (started) {
    unsigned long now = millis();
    if (shouldPlay() && now - lastUpdate >= delayMs) {
      lastUpdate = now;

      // compute a dynamic step based on ln(brightness)
      // lnMax normalizes ln() to [0..1]
      const float lnMax    = logf(256.0f);
      const float baseSpeed = energyBottom * 1.5f; // adjust this to speed up/down
      float        lnVal   = (brightness > 1.0f)
                           ? logf(brightness) 
                           : 0.0f;
      int          delta   = max(1, int((lnVal / lnMax) * baseSpeed));

      // advance brightness
      brightness += direction * delta;

      // clamp and reverse at ends
      if (brightness >= 255.0f) {
        brightness = 255.0f;
        direction = -1;
      }
      else if (brightness <= 0.0f) {
        brightness = 0.0f;
        direction = 1;
      }

      // apply to every pixel
      uint8_t bri = uint8_t(brightness);
      for (uint16_t i = 0; i < NeoPixel_1.numPixels(); ++i) {
        setPixelColor(NeoPixel_1, i, 255, 150, 255, bri);
      }
      NeoPixel_1.show();
    }

    if (!shouldPlay()) {
      started = false;
    }
  }
}

void setPixelColor(Adafruit_NeoPixel &strip,
                   uint16_t     idx,
                   uint8_t      r,
                   uint8_t      g,
                   uint8_t      b,
                   uint8_t      bri)
{
  // scale each channel by brightness
  uint8_t rr = (uint16_t(r) * bri) >> 8;
  uint8_t gg = (uint16_t(g) * bri) >> 8;
  uint8_t bb = (uint16_t(b) * bri) >> 8;
  strip.setPixelColor(idx, strip.Color(rr, gg, bb));
}