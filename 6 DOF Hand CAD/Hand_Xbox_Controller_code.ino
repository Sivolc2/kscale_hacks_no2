#include <Bluepad32.h> //board manager, need to use v4.1.0
#include <ESP32Servo.h> //library, need to use v3.0.6

//setuo servo with pins
Servo thumb_rotate_servo;
Servo thumb_grasp_servo;
Servo index_servo;
Servo middle_servo;
Servo ring_servo;
Servo pinky_servo;

//Servo PWM pins
const int thumb_rotate = 2;
const int thumb_grasp = 3;
const int index_pin = 4;
const int middle = 5;
const int ring = 6;
const int pinky = 7;

//Actuator ranges
const int thumb_rotate_open = 100;
const int thumb_rotate_closed = 180;

const int thumb_grasp_open = 116;
const int thumb_grasp_closed = 0;

const int index_open = 160;
const int index_closed = 0;

const int middle_open = 180;
const int middle_closed = 0;

const int ring_open = 180;
const int ring_closed = 0;

const int pinky_open = 180;
const int pinky_closed = 0;

//Motor values
int thumb_rotate_pos, thumb_grasp_pos, index_pos, middle_pos, ring_pos, pinky_pos, finger_curl;



ControllerPtr myControllers[BP32_MAX_GAMEPADS];

// This callback gets called any time a new gamepad is connected.
// Up to 4 gamepads can be connected at the same time.
void onConnectedController(ControllerPtr ctl) {
    bool foundEmptySlot = false;
    for (int i = 0; i < BP32_MAX_GAMEPADS; i++) {
        if (myControllers[i] == nullptr) {
            Serial.printf("CALLBACK: Controller is connected, index=%d\n", i);
            // Additionally, you can get certain gamepad properties like:
            // Model, VID, PID, BTAddr, flags, etc.
            ControllerProperties properties = ctl->getProperties();
            Serial.printf("Controller model: %s, VID=0x%04x, PID=0x%04x\n", ctl->getModelName().c_str(), properties.vendor_id,
                           properties.product_id);
            myControllers[i] = ctl;
            foundEmptySlot = true;
            break;
        }
    }
    if (!foundEmptySlot) {
        Serial.println("CALLBACK: Controller connected, but could not found empty slot");
    }
}

void onDisconnectedController(ControllerPtr ctl) {
    bool foundController = false;

    for (int i = 0; i < BP32_MAX_GAMEPADS; i++) {
        if (myControllers[i] == ctl) {
            Serial.printf("CALLBACK: Controller disconnected from index=%d\n", i);
            myControllers[i] = nullptr;
            foundController = true;
            break;
        }
    }

    if (!foundController) {
        Serial.println("CALLBACK: Controller disconnected, but not found in myControllers");
    }
}

void dumpGamepad(ControllerPtr ctl) {
     Serial.printf(
        "idx=%d, dpad: 0x%02x, buttons: 0x%04x, axis L: %4d, %4d, axis R: %4d, %4d, brake: %4d, throttle: %4d, "
        "misc: 0x%02x, gyro x:%6d y:%6d z:%6d, accel x:%6d y:%6d z:%6d\n",
        ctl->index(),        // Controller Index
        ctl->dpad(),         // D-pad
        ctl->buttons(),      // bitmask of pressed buttons
        ctl->axisX(),        // (-511 - 512) left X Axis
        ctl->axisY(),        // (-511 - 512) left Y axis
        ctl->axisRX(),       // (-511 - 512) right X axis
        ctl->axisRY(),       // (-511 - 512) right Y axis
        ctl->brake(),        // (0 - 1023): brake button
        ctl->throttle(),     // (0 - 1023): throttle (AKA gas) button
        ctl->miscButtons(),  // bitmask of pressed "misc" buttons
        ctl->gyroX(),        // Gyro X
        ctl->gyroY(),        // Gyro Y
        ctl->gyroZ(),        // Gyro Z
        ctl->accelX(),       // Accelerometer X
        ctl->accelY(),       // Accelerometer Y
        ctl->accelZ()        // Accelerometer Z
    );
}

void processGamepad(ControllerPtr ctl) {
    
    if (ctl->axisRX()> 20) {
      thumb_rotate_pos = map(ctl->axisRX(),0,511,thumb_rotate_open,thumb_rotate_closed);
      thumb_rotate_servo.write(max(thumb_rotate_pos,thumb_rotate_open));             
    }else if (ctl->axisRX() <= 20) {
      thumb_rotate_servo.write(thumb_rotate_open);
    }
    

    if ((ctl->brake() > 20) & (ctl->buttons()>63)) {
        finger_curl = map(ctl->brake(), 0, 1023, 180, 0);
        index_servo.write(min(finger_curl,160));    
        middle_servo.write(finger_curl);    
        ring_servo.write(finger_curl);    
        pinky_servo.write(finger_curl);    
    } else if ((ctl->brake() <= 20) & (ctl->buttons()>63)) {
      index_servo.write(index_open);    
      middle_servo.write(middle_open);    
      ring_servo.write(ring_open);    
      pinky_servo.write(pinky_open); 
    }

    if (ctl->throttle() > 20) {
      thumb_grasp_pos = map(ctl->throttle(), 0, 1023, thumb_grasp_open, thumb_grasp_closed);
      thumb_grasp_servo.write(thumb_grasp_pos);
      Serial.println(thumb_grasp_pos);
    } else if (ctl->throttle()) {
      thumb_grasp_servo.write(thumb_grasp_open);
    }
    Serial.println(ctl->buttons());

    if (ctl->a() & ctl->axisX() & (ctl->buttons() != 64)) {
      index_pos = map(ctl->axisX(), 70, 511, index_open, index_closed);
      index_servo.write(min(index_pos, index_open));
    } 

    if (ctl->b() & ctl->axisX() & (ctl->buttons() != 64)) {
      middle_pos = map(ctl->axisX(), 70, 511, middle_open, middle_closed);
      middle_servo.write(min(middle_pos, middle_open));
    } 
    if (ctl->x() & ctl->axisX() & (ctl->buttons() != 64)) {
      pinky_pos = map(ctl->axisX(), 70, 511, pinky_open, pinky_closed);
      pinky_servo.write(min(pinky_pos, pinky_open));
    } 
    if (ctl->y() & ctl->axisX() & (ctl->buttons() != 64)) {
      ring_pos = map(ctl->axisX(), 70, 511, ring_open, ring_closed);
      ring_servo.write(min(ring_pos, ring_open));
    } 


    //middle finger
    //hang loose

    //peace sign

    //pinch

    //point








    // Another way to query controller data is by getting the buttons() function.
    // See how the different "dump*" functions dump the Controller info.
    dumpGamepad(ctl);
}

void processControllers() {
    for (auto myController : myControllers) {
        if (myController && myController->isConnected() && myController->hasData()) {
            if (myController->isGamepad()) {
                processGamepad(myController);
            /*} else if (myController->isMouse()) {
                processMouse(myController);
            } else if (myController->isKeyboard()) {
                processKeyboard(myController);
            } else if (myController->isBalanceBoard()) {
                processBalanceBoard(myController);*/
            } else {
                Serial.println("Unsupported controller");
            }
        }
    }
}

/*
void dumpMouse(ControllerPtr ctl) {
    Serial.printf("idx=%d, buttons: 0x%04x, scrollWheel=0x%04x, delta X: %4d, delta Y: %4d\n",
                   ctl->index(),        // Controller Index
                   ctl->buttons(),      // bitmask of pressed buttons
                   ctl->scrollWheel(),  // Scroll Wheel
                   ctl->deltaX(),       // (-511 - 512) left X Axis
                   ctl->deltaY()        // (-511 - 512) left Y axis
    );
}

void dumpKeyboard(ControllerPtr ctl) {
    static const char* key_names[] = {
        // clang-format off
        // To avoid having too much noise in this file, only a few keys are mapped to strings.
        // Starts with "A", which is offset 4.
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
        "W", "X", "Y", "Z", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
        // Special keys
        "Enter", "Escape", "Backspace", "Tab", "Spacebar", "Underscore", "Equal", "OpenBracket", "CloseBracket",
        "Backslash", "Tilde", "SemiColon", "Quote", "GraveAccent", "Comma", "Dot", "Slash", "CapsLock",
        // Function keys
        "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
        // Cursors and others
        "PrintScreen", "ScrollLock", "Pause", "Insert", "Home", "PageUp", "Delete", "End", "PageDown",
        "RightArrow", "LeftArrow", "DownArrow", "UpArrow",
        // clang-format on
    };
    static const char* modifier_names[] = {
        // clang-format off
        // From 0xe0 to 0xe7
        "Left Control", "Left Shift", "Left Alt", "Left Meta",
        "Right Control", "Right Shift", "Right Alt", "Right Meta",
        // clang-format on
    };
    Serial.printf("idx=%d, Pressed keys: ", ctl->index());
    for (int key = Keyboard_A; key <= Keyboard_UpArrow; key++) {
        if (ctl->isKeyPressed(static_cast<KeyboardKey>(key))) {
            const char* keyName = key_names[key-4];
            Serial.printf("%s,", keyName);
       }
    }
    for (int key = Keyboard_LeftControl; key <= Keyboard_RightMeta; key++) {
        if (ctl->isKeyPressed(static_cast<KeyboardKey>(key))) {
            const char* keyName = modifier_names[key-0xe0];
            Serial.printf("%s,", keyName);
        }
    }
    Console.printf("\n");
}

void dumpBalanceBoard(ControllerPtr ctl) {
    Serial.printf("idx=%d,  TL=%u, TR=%u, BL=%u, BR=%u, temperature=%d\n",
                   ctl->index(),        // Controller Index
                   ctl->topLeft(),      // top-left scale
                   ctl->topRight(),     // top-right scale
                   ctl->bottomLeft(),   // bottom-left scale
                   ctl->bottomRight(),  // bottom-right scale
                   ctl->temperature()   // temperature: used to adjust the scale value's precision
    );
}

void processMouse(ControllerPtr ctl) {
    // This is just an example.
    if (ctl->scrollWheel() > 0) {
        // Do Something
    } else if (ctl->scrollWheel() < 0) {
        // Do something else
    }

    // See "dumpMouse" for possible things to query.
    dumpMouse(ctl);
}

void processKeyboard(ControllerPtr ctl) {
    if (!ctl->isAnyKeyPressed())
        return;

    // This is just an example.
    if (ctl->isKeyPressed(Keyboard_A)) {
        // Do Something
        Serial.println("Key 'A' pressed");
    }

    // Don't do "else" here.
    // Multiple keys can be pressed at the same time.
    if (ctl->isKeyPressed(Keyboard_LeftShift)) {
        // Do something else
        Serial.println("Key 'LEFT SHIFT' pressed");
    }

    // Don't do "else" here.
    // Multiple keys can be pressed at the same time.
    if (ctl->isKeyPressed(Keyboard_LeftArrow)) {
        // Do something else
        Serial.println("Key 'Left Arrow' pressed");
    }

    // See "dumpKeyboard" for possible things to query.
    dumpKeyboard(ctl);
}

void processBalanceBoard(ControllerPtr ctl) {
    // This is just an example.
    if (ctl->topLeft() > 10000) {
        // Do Something
    }

    // See "dumpBalanceBoard" for possible things to query.
    dumpBalanceBoard(ctl);
}
*/


// Arduino setup function. Runs in CPU 1
void setup() {
    Serial.begin(115200);
    Serial.printf("Firmware: %s\n", BP32.firmwareVersion());
    const uint8_t* addr = BP32.localBdAddress();
    Serial.printf("BD Addr: %2X:%2X:%2X:%2X:%2X:%2X\n", addr[0], addr[1], addr[2], addr[3], addr[4], addr[5]);

    // Setup the Bluepad32 callbacks
    BP32.setup(&onConnectedController, &onDisconnectedController);

    // "forgetBluetoothKeys()" should be called when the user performs
    // a "device factory reset", or similar.
    // Calling "forgetBluetoothKeys" in setup() just as an example.
    // Forgetting Bluetooth keys prevents "paired" gamepads to reconnect.
    // But it might also fix some connection / re-connection issues.
    BP32.forgetBluetoothKeys();

    // Enables mouse / touchpad support for gamepads that support them.
    // When enabled, controllers like DualSense and DualShock4 generate two connected devices:
    // - First one: the gamepad
    // - Second one, which is a "virtual device", is a mouse.
    // By default, it is disabled.
    BP32.enableVirtualDevice(false);

    
    thumb_rotate_servo.attach(thumb_rotate);
    thumb_rotate_servo.write(thumb_rotate_open);

    thumb_grasp_servo.attach(thumb_grasp);
    thumb_grasp_servo.write(thumb_grasp_open);

    index_servo.attach(index_pin);
    index_servo.write(index_open);

    middle_servo.attach(middle);
    middle_servo.write(middle_open);

    ring_servo.attach(ring);
    ring_servo.write(ring_open);

    pinky_servo.attach(pinky);
    pinky_servo.write(pinky_open);


}

// Arduino loop function. Runs in CPU 1.
void loop() {
    // This call fetches all the controllers' data.
    // Call this function in your main loop.
    bool dataUpdated = BP32.update();
    
    if (dataUpdated)
        processControllers();

    // The main loop must have some kind of "yield to lower priority task" event.
    // Otherwise, the watchdog will get triggered.
    // If your main loop doesn't have one, just add a simple `vTaskDelay(1)`.
    // Detailed info here:
    // https://stackoverflow.com/questions/66278271/task-watchdog-got-triggered-the-tasks-did-not-reset-the-watchdog-in-time

    //     vTaskDelay(1);
}
