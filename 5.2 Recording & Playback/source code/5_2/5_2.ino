#include <Arduino.h>
#include "ESP_I2S.h"

#define SAMPLE_RATE     (16000)
#define DATA_PIN        (GPIO_NUM_39)
#define CLOCK_PIN       (GPIO_NUM_38)
#define REC_TIME 5  //Recording time 5 seconds

void setup()
{
  uint8_t *wav_buffer;
  size_t wav_size;
  I2SClass i2s;
  I2SClass i2s1;
  Serial.begin(115200);
  pinMode(3, OUTPUT);
  i2s.setPinsPdmRx(CLOCK_PIN, DATA_PIN);
  if (!i2s.begin(I2S_MODE_PDM_RX, SAMPLE_RATE, I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO)) {
    Serial.println("Failed to initialize I2S PDM RX");
  }
  i2s1.setPins(45, 46, 42);
  if (!i2s1.begin(I2S_MODE_STD, SAMPLE_RATE, I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO)) {
    Serial.println("MAX98357 initialization failed!");
  }
  Serial.println("start REC");
  digitalWrite(3, HIGH);
  wav_buffer = i2s.recordWAV(REC_TIME, &wav_size);
  digitalWrite(3, LOW);
  //Play the recording
  i2s1.playWAV(wav_buffer, wav_size);
}

void loop()
{
  
}