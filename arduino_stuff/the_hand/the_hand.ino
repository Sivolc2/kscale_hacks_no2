#include <Servo.h>

// Create servo objects
Servo thumb;
Servo index_finger;
Servo middle_finger;
Servo ring_finger;
Servo pinky;
Servo wrist;

// Define pins
const int THUMB_PIN = 3;
const int INDEX_PIN = 5;
const int MIDDLE_PIN = 6;
const int RING_PIN = 9;
const int PINKY_PIN = 10;
const int WRIST_PIN = 11;

// Buffer for commands
char buffer[32];
int bufferIndex = 0;

void setup() {
  Serial.begin(9600);  // Start serial at standard speed
  
  // Attach all servos (simple attach)
  thumb.attach(THUMB_PIN);
  index_finger.attach(INDEX_PIN);
  middle_finger.attach(MIDDLE_PIN);
  ring_finger.attach(RING_PIN);
  pinky.attach(PINKY_PIN);
  wrist.attach(WRIST_PIN);
  
  // Move to starting position
  thumb.write(90);
  index_finger.write(90);
  middle_finger.write(90);
  ring_finger.write(90);
  pinky.write(90);
  wrist.write(90);
  
  delay(1000);  // Give servos time to move
  Serial.println("Ready");
}

void loop() {
  // Read serial commands
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      buffer[bufferIndex] = '\0';
      processCommand(buffer);
      bufferIndex = 0;
    } else {
      buffer[bufferIndex++] = c;
    }
  }
}

void processCommand(char* cmd) {
  char servo;
  int angle;
  
  if (sscanf(cmd, "%c,%d", &servo, &angle) == 2) {
    // Ensure angle is in valid range
    angle = constrain(angle, 0, 180);
    
    // Move the appropriate servo
    switch(servo) {
      case 'T':
        thumb.write(angle);
        break;
      case 'I':
        index_finger.write(angle);
        break;
      case 'M':
        middle_finger.write(angle);
        break;
      case 'R':
        ring_finger.write(angle);
        break;
      case 'P':
        pinky.write(angle);
        break;
      case 'W':
        wrist.write(angle);
        break;
    }
    
    delay(15);  // Small delay for servo to move
    Serial.println("OK");
  } else {
    Serial.println("ERR");
  }
}
