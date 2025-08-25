#include "leds.h"
#include "buzzers.h"

int pixelMelody = 0, pixelBass = 0;

Adafruit_NeoPixel NeoPixel_B(LED_LEN_BASS, LED_PIN_BASS, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel NeoPixel_M(LED_LEN_MELODY, LED_PIN_MELODY, NEO_GRB + NEO_KHZ800);

void initLed() {
  NeoPixel_B.begin();
  NeoPixel_M.begin();
  NeoPixel_B.show();
  NeoPixel_M.show();
}
void playLed(mpuData dataL, mpuData dataR) {
  // Map sensor values to pixel indices
  pixelMelody = map(dataL.ay, -17000, 17000, 0, LED_LEN_MELODY - 1);
  pixelBass = map(dataL.az, -17000, 17000, 0, LED_LEN_BASS - 1);

  // Ensure indices are within bounds
  pixelMelody = constrain(pixelMelody, 0, LED_LEN_MELODY - 1);
  pixelBass = constrain(pixelBass, 0, LED_LEN_BASS - 1);

  // Map gyroscope data to color components for melody
  int melodyR = map(dataL.gx, -17000, 17000, 0, 255);
  int melodyG = map(dataL.gy, -17000, 17000, 0, 255);
  int melodyB = map(dataL.gz, -17000, 17000, 0, 255);
  melodyR = constrain(melodyR, 0, 255);
  melodyG = constrain(melodyG, 0, 255);
  melodyB = constrain(melodyB, 0, 255);

  // Map gyroscope data to color components for bass (swap axes as desired)
  int bassR = map(dataR.gy, -17000, 17000, 0, 255);
  int bassG = map(dataR.gz, -17000, 17000, 0, 255);
  int bassB = map(dataR.gx, -17000, 17000, 0, 255);
  bassR = constrain(bassR, 0, 255);
  bassG = constrain(bassG, 0, 255);
  bassB = constrain(bassB, 0, 255);

  // Clear previous colors
  NeoPixel_M.clear();
  NeoPixel_B.clear();

  // Set new colors based on gyro-mapped RGB values
  NeoPixel_M.setPixelColor(pixelMelody, NeoPixel_M.Color(melodyR, melodyG, melodyB));
  NeoPixel_B.setPixelColor(pixelBass, NeoPixel_B.Color(bassR, bassG, bassB));
  NeoPixel_M.show();
  NeoPixel_B.show();
}

void playMelodyLEDs(){
  if(pixelMelody == LED_LEN_MELODY){
      pixelMelody = 0;
  }

  if (melodyCurrentNote.pitch < 7){
    switch (melodyCurrentNote.duration){
    case 250:
      NeoPixel_M.rainbow(pixelMelody, -1 , 255, 200, 1);
      break;
    case 500:
      NeoPixel_M.rainbow(pixelMelody, 1 , 255, 200, 1);
      break;
    case 1000:
      NeoPixel_M.rainbow(pixelMelody, 2 , 255, 200, 1);
      break;    
    default:
      NeoPixel_M.rainbow(pixelMelody, 3 , 255, 200, 1);
      break;
    }
    NeoPixel_M.show();
    pixelMelody++;
  } else {
    for(int pixel = 0; pixel<LED_LEN_MELODY; pixel++){
        NeoPixel_M.setPixelColor(pixel, NeoPixel_M.Color(255, 255, 255));
    }
    NeoPixel_M.show();
  }
}

void playBassLEDs(){
  if (pixelBass == LED_LEN_BASS){
    pixelBass = 0;
  }

  if (bassCurrentNote.pitch < 7){
    switch (bassCurrentNote.duration){
    case 1000:
      NeoPixel_B.fill(100, 0, LED_LEN_BASS);
      break;
    case 2000:
      NeoPixel_B.fill(200, 0, LED_LEN_BASS);
      break;
    case 4000:
      NeoPixel_B.fill(50, 0, LED_LEN_BASS);
      break;    
    default:
      NeoPixel_B.fill(150, 0, LED_LEN_BASS);
      break;
    }
    NeoPixel_B.show();
    pixelBass++;
  } else {
    for(int pixel = 0; pixel<LED_LEN_BASS; pixel++){
        NeoPixel_B.setPixelColor(pixel, NeoPixel_B.Color(255, 0, 0));
    }
    NeoPixel_B.show();
  }
}
