#include <Servo.h>

// Create array of 6 servo objects for all fingers including both thumb joints
Servo fingers[6];
// Pin mapping: thumb1, thumb2, index, middle, ring, pinky
const int SERVO_PINS[6] = {3, 5, 6, 9, 10, 11};  // Both thumb servos and fingers

// Custom angle ranges for each finger
const int MIN_ANGLES[6] = {180, 0, 10, 10, 10, 10};      // Open positions (start position)
const int MAX_ANGLES[6] = {110, 100, 160, 170, 170, 170};  // Closed positions

// Track the state of each finger (true = open, false = closed)
bool fingerStates[6] = {true, true, true, true, true, true};  // Start all fingers open

void setup() {
  Serial.begin(9600);
  
  // Initialize each servo
  for (int i = 0; i < 6; i++) {
    fingers[i].attach(SERVO_PINS[i]);
    fingers[i].write(MIN_ANGLES[i]); // Start at open position
    fingerStates[i] = true;     // Start all fingers open
  }
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    int fingerIndex = -1;
    
    // Map keys to fingers (left to right: q,w,e,r,t,y)
    switch(cmd) {
      case 'q': fingerIndex = 0; break;  // thumb2 (pin 3)  - Range: 180° to 110°
      case 'w': fingerIndex = 1; break;  // thumb1 (pin 5)  - Range: 0° to 100°
      case 'e': fingerIndex = 2; break;  // index (pin 6)   - Range: 10° to 160°
      case 'r': fingerIndex = 3; break;  // middle (pin 9)  - Range: 10° to 170°
      case 't': fingerIndex = 4; break;  // ring (pin 10)   - Range: 10° to 170°
      case 'y': fingerIndex = 5; break;  // pinky (pin 11)  - Range: 10° to 170°
    }
    
    if (fingerIndex >= 0) {
      // Toggle finger state and position
      fingerStates[fingerIndex] = !fingerStates[fingerIndex];
      int newPos = fingerStates[fingerIndex] ? MIN_ANGLES[fingerIndex] : MAX_ANGLES[fingerIndex];
      fingers[fingerIndex].write(newPos);
      
      // Send back confirmation
      Serial.print("Finger ");
      Serial.print(fingerIndex);
      Serial.print(" ");
      Serial.print(fingerStates[fingerIndex] ? "opened" : "closed");
      Serial.print(" (");
      Serial.print(newPos);
      Serial.println("°)");
    }
  }
  delay(15); // Small delay to prevent overwhelming the serial
}
