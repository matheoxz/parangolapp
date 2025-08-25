#include "buzzers.h"

unsigned long previousMillisMelody = 0, previousMillisBass = 0;
struct note melodyCurrentNote = {0, 3, 0, false};
struct note bassCurrentNote = {0, 0, 0, false};

int noteDuration[] = NOTE_DURATIONS;
int bb_scale[6][8] = Bb_SCALE;

/**
 * @brief Determines the duration of a note based on the total acceleration.
 *
 * This function takes the total acceleration as input and returns a note duration
 * based on predefined ranges of acceleration values. The note duration is selected
 * randomly from specific ranges within the `noteDuration` array.
 *
 * @param totalAcc The total acceleration value.
 * @return The duration of the note, selected randomly from predefined ranges.
 */
int defineNoteDuration (float totalAcc){
  if (totalAcc > 0.5 and totalAcc < 0.75) return noteDuration[random(18, 19)];
  if (totalAcc > 0.75 and totalAcc < 3) return noteDuration[random(10, 18)];
  return noteDuration[random(0, 10)];
}

/**
 * @brief Adjusts the melody note based on accelerometer and gyroscope readings.
 *
 * This function modifies the current melody note's octave and pitch based on the 
 * provided total acceleration and total spin values. The adjustments are made 
 * according to specific thresholds and random variations.
 *
 * @param totalAcc The total acceleration value from the accelerometer.
 * @param totalSpin The total spin value from the gyroscope.
 */
void defineMelodyNote(float totalAcc, float totalSpin){
  int octave = melodyCurrentNote.octave;
  int pitch = melodyCurrentNote.pitch;

  if (totalAcc < 3) octave -= 1;
  if (totalAcc >= 3) octave += 1;

  if (octave < 0) octave = 5;
  if (octave > 5) octave = 2;
  
  if (totalSpin < 3) pitch -= random(0, 6);
  if (totalSpin > 4) pitch += random(0, 6);

  if (pitch < 0) pitch = abs(pitch);
  while (pitch > 6) pitch -= 3;

  melodyCurrentNote.pitch = pitch;
  melodyCurrentNote.octave = octave;
  melodyCurrentNote.duration = defineNoteDuration(totalAcc);

  if(totalAcc < 0.5 || totalSpin < 0.5) {
    melodyCurrentNote.pitch = 7;
    melodyCurrentNote.duration = 50;
  }
}

/**
 * @brief Defines the bass note based on the total acceleration and total spin.
 *
 * This function adjusts the octave and pitch of the bass note according to the 
 * provided total acceleration and total spin values. The pitch is selected from 
 * a predefined set of harmonics based on the current melody note's pitch. The 
 * octave is adjusted based on the total spin value, and the duration of the note 
 * is determined by the total acceleration.
 *
 * @param totalAcc The total acceleration value used to define the note duration.
 * @param totalSpin The total spin value used to adjust the octave.
 */
void defineBassNote(float totalAcc, float totalSpin){
  int harmonics[8][3] = {{2, 4, 6}, {3, 5, 0}, {4, 6, 1}, 
                        {5, 0, 2}, {6, 1, 3}, {0, 2, 4}, 
                        {1, 3, 5}, {0, 2, 4}};
  int octave = bassCurrentNote.octave;
  int pitch = bassCurrentNote.pitch;

  if (totalSpin < 3) octave -= 1;
  if (totalSpin >= 3) octave += 1;

  if (octave < 0) octave = 2;
  if (octave > 5) octave = 0;
  
  bassCurrentNote.pitch = harmonics[melodyCurrentNote.pitch][random(0, 2)];
  bassCurrentNote.octave = octave;
  bassCurrentNote.duration = defineNoteDuration(totalAcc) * 2;

  if(totalAcc < 0.5 || totalSpin < 0.5) {
    bassCurrentNote.pitch = 7;
    bassCurrentNote.duration = 50;
  }
}

void playBassNote(mpuData mpuData){
  float totalAcc = sqrt(mpuData.ax * mpuData.ax + mpuData.ay * mpuData.ay);
  float totalSpin = sqrt(mpuData.gx * mpuData.gx + mpuData.gy * mpuData.gy);

  defineBassNote(totalAcc, totalSpin);
  tone(BUZZZER_PIN_2, bb_scale[bassCurrentNote.octave][bassCurrentNote.pitch]);
  bassCurrentNote.is_playing = true;
  playBassLEDs();
}

void playMelodyNote(mpuData mpuData){
  float totalAcc = sqrt(mpuData.ax * mpuData.ax + mpuData.ay * mpuData.ay);
  float totalSpin = sqrt(mpuData.gx * mpuData.gx + mpuData.gy * mpuData.gy);

  defineMelodyNote(totalAcc, totalSpin);
  tone(BUZZZER_PIN_1, bb_scale[melodyCurrentNote.octave][melodyCurrentNote.pitch]);
  melodyCurrentNote.is_playing = true;
  playMelodyLEDs();
}