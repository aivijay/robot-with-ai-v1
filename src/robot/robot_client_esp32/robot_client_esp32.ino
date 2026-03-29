#!/usr/bin/env python3
"""
robot_client_esp32.py — ESP32-CAM thin client
Runs on ESP32-CAM hardware.
Streams JPEG frames to laptop and receives motor commands via HTTP.

Wiring (ESP32-CAM → DRV8833):
  3.3V ─────────── VCC (logic)
  GND ─────────── GND
  GPIO 4 ───────── AIN1
  GPIO 2 ───────── AIN2
  GPIO 12 ──────── BIN1
  GPIO 13 ──────── BIN2
  VMOT ────────── Battery 3.7-6V

Upload with Arduino IDE or PlatformIO.
Requires: esp32 board support, WiFi, HTTPClient, ESP32Camera
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <esp_camera.h>

// ==== WIFI CONFIG ====
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASS = "YOUR_WIFI_PASSWORD";
const char* LAPTOP_HOST = "192.168.1.100";  // CHANGE THIS
const int LAPTOP_PORT = 8000;

// ==== MOTOR PINS (ESP32-CAM GPIO) ====
#define AIN1 4
#define AIN2 2
#define BIN1 12
#define BIN2 13

// Motor state
bool motorRunning = false;
unsigned long lastCommandTime = 0;
const unsigned long COMMAND_TIMEOUT_MS = 5000;

// Forward declarations
void setMotors(int8_t leftSpeed, int8_t rightSpeed);
void sendFrame();
void pollCommand();

void setup() {
  Serial.begin(115200);

  // Motor pins
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  setMotors(0, 0);

  // Camera config for ESP32-CAM (AI-Thinker module)
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = 3;   // Y2
  config.pin_d1 = 1;   // Y3
  config.pin_d2 = 13;  // Y4
  config.pin_d3 =  14; // Y5
  config.pin_d4 =  15; // Y6
  config.pin_d5 =  16; // Y7
  config.pin_xclk = 10; // XCLK
  config.pin_pclk = 8;  // PCLK
  config.pin_vsync = 9; // VSYNC
  config.pin_href = 11; // HREF
  config.pin_sscb_sda = 18; // SIOD
  config.pin_sscb_scl = 17; // SIOC
  config.pin_reset = -1;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_VGA;  // 640x480
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAM_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 2;

  // Check PSRAM
  if (psramFound()) {
    config.fb_location = CAM_FB_IN_PSRAM;
  } else {
    config.fb_location = CAM_FB_IN_DRAM;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed: 0x%x\n", err);
    return;
  }
  Serial.println("Camera OK");

  // WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Connecting WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected. IP: " + WiFi.localIP());
}

void loop() {
  // Send frame to laptop
  sendFrame();

  // Poll for command
  pollCommand();

  // Safety: stop if command timeout
  if (millis() - lastCommandTime > COMMAND_TIMEOUT_MS) {
    setMotors(0, 0);
  }

  delay(200);  // ~5 FPS
}

// --- Motor helpers ---
void setMotors(int8_t leftSpeed, int8_t rightSpeed) {
  // leftSpeed, rightSpeed: -100 to 100
  // ESP32-CAM GPIO4=AIN1, GPIO2=AIN2 for left motor
  // ESP32-CAM GPIO12=BIN1, GPIO13=BIN2 for right motor

  // Left motor
  if (leftSpeed > 0) {
    digitalWrite(AIN1, HIGH);
    digitalWrite(AIN2, LOW);
    ledcWrite(AIN1, leftSpeed * 2.55);  // PWM on AIN1
  } else if (leftSpeed < 0) {
    digitalWrite(AIN1, LOW);
    digitalWrite(AIN2, HIGH);
    ledcWrite(AIN2, (-leftSpeed) * 2.55);
  } else {
    digitalWrite(AIN1, LOW);
    digitalWrite(AIN2, LOW);
  }

  // Right motor
  if (rightSpeed > 0) {
    digitalWrite(BIN1, HIGH);
    digitalWrite(BIN2, LOW);
    ledcWrite(BIN1, rightSpeed * 2.55);
  } else if (rightSpeed < 0) {
    digitalWrite(BIN1, LOW);
    digitalWrite(BIN2, HIGH);
    ledcWrite(BIN2, (-rightSpeed) * 2.55);
  } else {
    digitalWrite(BIN1, LOW);
    digitalWrite(BIN2, LOW);
  }
}

// --- Send camera frame to laptop ---
void sendFrame() {
  camera_fb_t* fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    return;
  }

  if (fb->format != PIXFORMAT_JPEG) {
    esp_camera_fb_return(fb);
    return;
  }

  WiFiClient* client = new WiFiClient();
  HTTPClient http;
  String url = String("http://") + LAPTOP_HOST + ":" + LAPTOP_PORT + "/api/frame";

  if (http.begin(*client, url)) {
    http.addHeader("Content-Type", "image/jpeg");
    int httpCode = http.sendRequest("POST", fb->buf, fb->len);
    http.end();
  }
  delete client;
  esp_camera_fb_return(fb);
}

// --- Poll laptop for motor command ---
void pollCommand() {
  WiFiClient* client = new WiFiClient();
  HTTPClient http;
  String url = String("http://") + LAPTOP_HOST + ":" + LAPTOP_PORT + "/api/command";

  if (http.begin(*client, url)) {
    int httpCode = http.GET();
    if (httpCode == 200) {
      String payload = http.getString();
      // Expected: {"direction":"forward","speed":80}
      lastCommandTime = millis();

      // Simple JSON parsing (no library needed)
      if (payload.indexOf("forward") > 0) {
        int speed = 80;
        int sp = payload.indexOf("speed");
        if (sp > 0) {
          // crude extraction
          speed = payload.substring(sp + 6).toInt();
          if (speed > 100) speed = 100;
        }
        setMotors(speed, speed);
      } else if (payload.indexOf("left") > 0) {
        setMotors(-60, 60);
      } else if (payload.indexOf("right") > 0) {
        setMotors(60, -60);
      } else if (payload.indexOf("backward") > 0) {
        setMotors(-70, -70);
      } else if (payload.indexOf("stop") > 0) {
        setMotors(0, 0);
      }
    }
    http.end();
  }
  delete client;
}
