#include <Arduino.h>
#include "pitches.h"
#include "mpu.h"
#include "leds.h"

#define BUZZZER_PIN_1  25
#define BUZZZER_PIN_2  26

struct note
{
  int pitch;
  int octave;
  int duration;
  bool is_playing;
};


// defines  Bb Major scale with 6 octaves
#define Bb_SCALE {{NOTE_AS1, NOTE_C1, NOTE_D1, NOTE_DS1, NOTE_F1, NOTE_G1, NOTE_A1, SILENCE}, \
                {NOTE_AS2, NOTE_C2, NOTE_D2, NOTE_DS2, NOTE_F2, NOTE_G2, NOTE_A2, SILENCE}, \
                {NOTE_AS3, NOTE_C3, NOTE_D3, NOTE_DS3, NOTE_F3, NOTE_G3, NOTE_A3, SILENCE}, \
                {NOTE_AS4, NOTE_C4, NOTE_D4, NOTE_DS4, NOTE_F4, NOTE_G4, NOTE_A4, SILENCE},\
                {NOTE_AS5, NOTE_C5, NOTE_D5, NOTE_DS5, NOTE_F5, NOTE_G5, NOTE_A5, SILENCE},\
                {NOTE_AS6, NOTE_C6, NOTE_D6, NOTE_DS6, NOTE_F6, NOTE_G6, NOTE_A6, SILENCE}};

#define NOTE_DURATIONS {125, 125, 125, 125, 125, 125, 125, 125, 250, 250, 250, 250, 500, 500, 500, 500, 1000, 1000, 1000, 1500};


extern unsigned long previousMillisMelody, previousMillisBass;
extern struct note melodyCurrentNote;
extern struct note bassCurrentNote;

void playBassNote(mpuData mpuData);
void playMelodyNote(mpuData mpuData);