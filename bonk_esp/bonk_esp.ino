// ESP32 Double-Buffer Sampling mit esp_timer
// Mikrofon an GPIO 34 (Achtung: GPIO34 ist input-only)
// Burst = 512 Samples, Abtastrate ~1 kHz
#include <Arduino.h>
#include "esp_timer.h"

const int micPin = 34;
const int BURST_SIZE = 1024;
const uint32_t SAMPLE_PERIOD_US = 250; // 1000 µs -> 1 kHz

static uint16_t bufferA[BURST_SIZE];
static uint16_t bufferB[BURST_SIZE];

volatile uint16_t *completedBuf = nullptr;
volatile bool bufferReady = false;
bool useBufferA = true;

portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;
volatile int sampleIndex = 0;
esp_timer_handle_t periodic_timer;

// Timer-Callback (wird im esp_timer-Kontext aufgerufen)
void sample_cb(void* arg) {
  uint16_t sample = (uint16_t)analogRead(micPin);

  if (useBufferA) bufferA[sampleIndex] = sample;
  else            bufferB[sampleIndex] = sample;

  sampleIndex++;
  if (sampleIndex >= BURST_SIZE) {
    // Puffer voll -> markieren, Wechsel auf anderes Puffer
    portENTER_CRITICAL(&timerMux);
    completedBuf = useBufferA ? bufferA : bufferB; // das gerade gefüllte
    useBufferA = !useBufferA;                     // ab jetzt im anderen Puffer aufnehmen
    bufferReady = true;
    sampleIndex = 0;
    portEXIT_CRITICAL(&timerMux);
  }
}

void setup() {
  Serial.begin(921600);
  delay(200);

  // ADC-Feinheiten (optional)
  analogReadResolution(10);            // 0..1023
  analogSetPinAttenuation(micPin, ADC_11db);

  // esp_timer konfigurieren
  esp_timer_create_args_t periodic_timer_args = {
    .callback = &sample_cb,
    .arg = nullptr,
    .name = "sample_timer"
  };

  if (esp_timer_create(&periodic_timer_args, &periodic_timer) != ESP_OK) {
    Serial.println("esp_timer_create failed");
    while (true) delay(1000);
  }
  // periodisch starten (Argument in Mikrosekunden)
  if (esp_timer_start_periodic(periodic_timer, SAMPLE_PERIOD_US) != ESP_OK) {
    Serial.println("esp_timer_start_periodic failed");
    while (true) delay(1000);
  }

  Serial.println("Sampler ready");
}

void loop() {
  // Sobald ein kompletter Burst bereit ist, wird er per Serial gesendet
  if (bufferReady) {
    uint16_t *buf;
    portENTER_CRITICAL(&timerMux);
    buf = (uint16_t*)completedBuf;
    bufferReady = false;
    portEXIT_CRITICAL(&timerMux);

    // Sende-Format: <START>v1,v2,v3,...,vN<END>\n
    Serial.print("<START>");
    for (int i = 0; i < BURST_SIZE; ++i) {
      Serial.print(buf[i]);
      if (i < BURST_SIZE - 1) Serial.print(",");
    }
    Serial.println("<END>");
  }
}
