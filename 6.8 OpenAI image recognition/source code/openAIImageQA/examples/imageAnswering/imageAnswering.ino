#include <WiFi.h>
#include <OpenAI.h>
#include "camera.h"
#include "wav_header.h"
#include <Arduino.h>
#include <SPI.h>
#include "FS.h"
#include "SD.h"
#include "SPI.h"
#include "ESP_I2S.h"
#define BUTTON_PIN 0
#define LED_PIN 3
#define SAMPLE_RATE     (16000)
#define DATA_PIN        (GPIO_NUM_39)
#define CLOCK_PIN       (GPIO_NUM_38)


const char* ssid = "";
const char* password = "";
const char* api_key = "";

OpenAI openai(api_key);
OpenAI_ChatCompletion chat(openai);
OpenAI_AudioTranscription audio(openai);
OpenAI_TTS tts(openai);
I2SClass I2S;
bool isRecording = false; 
uint8_t *wavBuffer = NULL;
size_t wavBufferSize = 0; 

void setup(){
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  audioInit();
  initCamera();
  WiFi.begin(ssid, password);
  Serial.print("Connecting");
  while (WiFi.status() != WL_CONNECTED) { 
    delay(100);
    Serial.print(".");
  }
  Serial.println("success!");
  chatInit();
  digitalWrite(LED_PIN, HIGH);
}
void loop() {
    if (digitalRead(BUTTON_PIN) == LOW) {
        if (!isRecording) {
            startRecording();
        }
    } else {
        if (isRecording) {
            stopRecording();
        }
    }
    if (isRecording) {
        size_t bytesAvailable = I2S.available();
        if (bytesAvailable > 0) {
            uint8_t *newBuffer = (uint8_t *)realloc(wavBuffer, wavBufferSize + bytesAvailable);
            if (newBuffer == NULL) {
                log_e("Failed to reallocate WAV buffer");
                stopRecording();
                return;
            }
            wavBuffer = newBuffer;

            size_t bytesRead = I2S.readBytes((char *)(wavBuffer + wavBufferSize), bytesAvailable);
            wavBufferSize += bytesRead;
        }
    }

    delay(10); 
}
void audioInit()
{
  I2S.setPinsPdmRx(CLOCK_PIN, DATA_PIN);
  if (!I2S.begin(I2S_MODE_PDM_RX, SAMPLE_RATE, I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO)) {
    Serial.println("Failed to initialize I2S PDM RX");
  }
}
void chatInit()
{
  chat.setModel("gpt-4o-mini");   //Model to use for completion. Default is gpt-4-vision-preview is needed for image analysis
  chat.setSystem("Code geek");      //Description of the required assistant
  chat.setMaxTokens(1000);          //The maximum number of tokens to generate in the completion.
  chat.setTemperature(0.2);         //float between 0 and 2. Higher value gives more random results.
  chat.setStop("\r");               //Up to 4 sequences where the API will stop generating further tokens.
  chat.setPresencePenalty(0);       //float between -2.0 and 2.0. Positive values increase the model's likelihood to talk about new topics.
  chat.setFrequencyPenalty(0);      //float between -2.0 and 2.0. Positive values decrease the model's likelihood to repeat the same line verbatim.
  chat.setUser("OpenAI-ESP32-cam");     //A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse.
}

String SpeechToText()
{
  String  txt = audio.file(wavBuffer,wavBufferSize,(OpenAI_Audio_Input_Format)5);
  free(wavBuffer);
  wavBuffer = NULL;
  wavBufferSize = 0;
  return txt;
}

String imageAnswering(String txt)
{
  camera_fb_t *fb = NULL; 
  String response;
  // Take Picture with Camera and return pointer to image buffer
  fb = esp_camera_fb_get();
  Serial.println("capuring image");
  delay(5);
  esp_camera_fb_return(fb);
  delay(1000);
  Serial.println("sending image to openai");
  OpenAI_StringResponse result = chat.message(txt,fb->buf,fb->len); // enter your prompt with the image buffer and the length of the buffer

  if(result.length() >= 1){
    for (unsigned int i = 0; i < result.length(); ++i){
      response = result.getAt(i);
      response.trim();
    }
  }
  return response;
}

int TextToSpeech(String txt)
{
  return tts.message(txt);
}

void startRecording() {
    size_t sampleRate = I2S.rxSampleRate();
    uint16_t sampleWidth = (uint16_t)I2S.rxDataWidth();
    uint16_t numChannels = (uint16_t)I2S.rxSlotMode();

    wavBufferSize = 0;
    wavBuffer = (uint8_t *)malloc(PCM_WAV_HEADER_SIZE);
    if (wavBuffer == NULL) {
        log_e("Failed to allocate WAV buffer");
        return;
    }

    const pcm_wav_header_t wavHeader = PCM_WAV_HEADER_DEFAULT(0, sampleWidth, sampleRate, numChannels);
    memcpy(wavBuffer, &wavHeader, PCM_WAV_HEADER_SIZE);
    wavBufferSize = PCM_WAV_HEADER_SIZE;

    Serial.println("Start recording...");
    isRecording = true;
}

void stopRecording() {
    if (!isRecording) return;

    isRecording = false;
    Serial.printf("Stop recording. Total recorded size: %u\n", wavBufferSize);

    pcm_wav_header_t *header = (pcm_wav_header_t *)wavBuffer;
    header->descriptor_chunk.chunk_size =  (wavBufferSize) + sizeof(pcm_wav_header_t) - 8;
    header->data_chunk.subchunk_size = wavBufferSize - PCM_WAV_HEADER_SIZE;

    Serial.println("Start speech to text! ");
    String txt = SpeechToText();
    if(txt!=NULL){
        Serial.printf("SpeechToText Message:\n%s\n", txt.c_str());
        Serial.println("Start image Answering! ");
        txt=imageAnswering(txt);
        if(txt!=NULL){
          Serial.printf("imageAnswering Message:\n%s\n", txt.c_str());
          Serial.println("Start text to audio! ");
          if(TextToSpeech(txt)==-1){
            Serial.println("Audio reception failed! ");
          }
        }else{
          Serial.println("imageAnswering failed!");
        }
    }else{
      Serial.println("speech to text failed!");
    }
}

