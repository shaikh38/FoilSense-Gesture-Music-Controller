const int touchPin = 4;  // GPIO 4

int baseline = 0;
const float touchThresholdFactor = 0.85f;
const float releaseThresholdFactor = 0.90f;

unsigned long pressStart = 0;
unsigned long lastTapTime = 0;
bool isPressed = false;
int tapCount = 0;

const unsigned long holdDuration = 1000;        // ms
const unsigned long doubleTapMaxInterval = 400; // ms
const unsigned long debounceDelay = 50;

unsigned long lastChange = 0;
  void setup() {
  Serial.begin(9600);
  delay(1000);
  Serial.println("Calibrating baseline... Don't touch pad");
  baseline = calibrateBaseline(touchPin);
  Serial.print("Baseline: ");
  Serial.println(baseline);
  Serial.println("Start touching pad");
}

int calibrateBaseline(int pin) {
  long sum = 0;
  const int samples = 80;
  for (int i = 0; i < samples; i++) {
    sum += touchRead(pin);
    delay(5);
  }
  int base = sum / samples;
  if (base == 0) base = 1;  // avoid zero baseline
  return base;
}

void loop() {
  int val = touchRead(touchPin);
  int touchThreshold = baseline * touchThresholdFactor;
  int releaseThreshold = baseline * releaseThresholdFactor;
  unsigned long now = millis();

  if (isPressed) {
    if (val > releaseThreshold && (now - lastChange) > debounceDelay) {
      isPressed = false;
      if ((now - pressStart) >= holdDuration) {
        Serial.println("LONG PRESS");
        tapCount = 0;
      } else {
        tapCount++;
        lastTapTime = now;
      }
      lastChange = now;
    }
  } else {
    if (val < touchThreshold && (now - lastChange) > debounceDelay) {
      isPressed = true;
      pressStart = now;
      lastChange = now;
      // Removed "Touch detected" print here
    }

    // OUTPUT tap results after window passes
    if (tapCount > 0 && (now - lastTapTime) > doubleTapMaxInterval) {
      if (tapCount == 1) {
        Serial.println("SINGLE TAP");
      } else if (tapCount >= 2) {
        Serial.println("DOUBLE TAP");
      }
      tapCount = 0;
    }
  }
  delay(20);
}
