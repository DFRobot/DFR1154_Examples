#include "esp_camera.h"
#include "FS.h"
#include "SD.h"
#include "driver/rtc_io.h"
#include "esp_sleep.h"

#define SD_CARD_CS   10

#define PWDN_GPIO_NUM     -1
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM     5
#define Y9_GPIO_NUM       4
#define Y8_GPIO_NUM       6
#define Y7_GPIO_NUM       7
#define Y6_GPIO_NUM       14
#define Y5_GPIO_NUM       17
#define Y4_GPIO_NUM       21
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM       16
#define VSYNC_GPIO_NUM    1
#define HREF_GPIO_NUM     2
#define PCLK_GPIO_NUM     15
#define SIOD_GPIO_NUM  8
#define SIOC_GPIO_NUM  9

#define TIME_TO_SLEEP  25 // Shooting interval time (S)
#define uS_TO_S_FACTOR 1000000ULL
#define SLEEP_DURATION (TIME_TO_SLEEP * uS_TO_S_FACTOR)

RTC_DATA_ATTR int photo_count = 0; // Use RTC memory to save counts (lost in case of power failure)

bool initCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = Y2_GPIO_NUM;
  config.pin_d1       = Y3_GPIO_NUM;
  config.pin_d2       = Y4_GPIO_NUM;
  config.pin_d3       = Y5_GPIO_NUM;
  config.pin_d4       = Y6_GPIO_NUM;
  config.pin_d5       = Y7_GPIO_NUM;
  config.pin_d6       = Y8_GPIO_NUM;
  config.pin_d7       = Y9_GPIO_NUM;
  config.pin_xclk     = XCLK_GPIO_NUM;
  config.pin_pclk     = PCLK_GPIO_NUM;
  config.pin_vsync    = VSYNC_GPIO_NUM;
  config.pin_href     = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn     = PWDN_GPIO_NUM;
  config.pin_reset    = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_UXGA;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 10;
  config.fb_count = 2;
  config.grab_mode = CAMERA_GRAB_LATEST;
  
  esp_err_t err = esp_camera_init(&config);

  sensor_t *s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1);        // flip it back
    s->set_brightness(s, 1);   // up the brightness just a bit
    s->set_saturation(s, -2);  // lower the saturation
  }
  
  return err == ESP_OK;
}

bool initSDCard() {
  if (!SD.begin(SD_CARD_CS)) {
    return false;
  }
  uint8_t cardType = SD.cardType();
  return cardType != CARD_NONE;
}

void takePhotoAndSave() {
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Failed to obtain the image.");
    return;
  }

  String path = "/photo_" + String(photo_count) + ".jpg";
  fs::FS &fs = SD;
  File file = fs.open(path.c_str(), FILE_WRITE);
  if (!file) {
    Serial.println("Save failed");
  } else {
    file.write(fb->buf, fb->len);
    Serial.println("Photo saving path: " + path);
  }
  file.close();
  esp_camera_fb_return(fb);

  photo_count++; // The number of the next picture
}

void setup() {
  Serial.begin(115200);
  delay(3000); // Give the serial port some startup time

  if (!initCamera()) {
    Serial.println("The camera initialization failed.");
    return;
  }

  if (!initSDCard()) {
    Serial.println("The initialization of the SD card failed.");
    return;
  }
  pinMode(3,OUTPUT);
  digitalWrite(3,HIGH);
  takePhotoAndSave();
  //delay(500);
  digitalWrite(3,LOW);
  Serial.println("Get ready to enter deep sleep.");
  esp_sleep_enable_timer_wakeup(SLEEP_DURATION);
  esp_deep_sleep_start();
}

void loop() {
  // It won't be executed up to here.
}
