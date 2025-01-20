#!/usr/bin/env python3
import serial
import sys
import tty
import termios
import time
import glob
import serial.tools.list_ports
from queue import Queue
from threading import Thread, Lock

def find_arduino_port():
    """Find the Arduino port on macOS."""
    # First try to find Arduino by checking port descriptions
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if any(id in port.description.lower() for id in ['arduino', 'usb serial', 'cu.usbmodem']):
            return port.device
    
    # If not found by description, try common macOS patterns
    if sys.platform == 'darwin':
        possible_ports = glob.glob('/dev/cu.usbmodem*') + glob.glob('/dev/cu.usbserial*')
        if possible_ports:
            return possible_ports[0]
    
    # If still not found, show available ports
    if ports:
        print("\nAvailable ports:")
        for port in ports:
            print(f"- {port.device}: {port.description}")
    
    return '/dev/cu.usbmodem*'  # Default macOS pattern

class HandController:
    def __init__(self, port=None, baud_rate=9600):
        """Initialize the hand controller with the specified serial port."""
        if port is None:
            port = find_arduino_port()
        
        try:
            self.ser = serial.Serial(port, baud_rate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            print(f"Connected to Arduino on {port}")
            # Initialize finger states (False = closed, True = open)
            self.finger_states = [False] * 6  # Updated to 6 for both thumb servos
            self.finger_names = ["Thumb2", "Thumb1", "Index", "Middle", "Ring", "Pinky"]
            self.finger_keys = ['q', 'w', 'e', 'r', 't', 'y']
            
            # Initialize command queue and processing thread
            self.command_queue = Queue()
            self.state_lock = Lock()
            self.running = True
            self.command_thread = Thread(target=self._process_command_queue, daemon=True)
            self.command_thread.start()
            
        except serial.SerialException as e:
            print(f"Error opening serial port {port}: {e}")
            print("\nTroubleshooting tips:")
            print("1. Make sure the Arduino is connected")
            print("2. Check if the Arduino shows up in System Information")
            print("3. Verify the Arduino has the correct sketch uploaded")
            sys.exit(1)

    def _process_command_queue(self):
        """Process commands from the queue with proper timing."""
        while self.running:
            try:
                if not self.command_queue.empty():
                    cmd, desired_state = self.command_queue.get()
                    self._send_command_direct(cmd, desired_state)
                    time.sleep(0.02)  # 20ms delay between commands
                else:
                    time.sleep(0.01)  # Small sleep when queue is empty
            except Exception as e:
                print(f"Error processing command queue: {e}")

    def _send_command_direct(self, cmd, desired_state=None):
        """Internal method to directly send command to Arduino."""
        try:
            finger_index = self.finger_keys.index(cmd.lower())
            
            # If desired_state is provided, only send command if needed
            if desired_state is not None:
                with self.state_lock:
                    current_state = self.finger_states[finger_index]
                    if current_state == desired_state:
                        return  # State already matches, no need to send command
            
            self.ser.write(cmd.encode())
            response = self.ser.readline().decode().strip()
            if response:
                print(response)
                # Update local state based on Arduino response
                with self.state_lock:
                    self.finger_states[finger_index] = not self.finger_states[finger_index]
                    self.display_status()
        except serial.SerialException as e:
            print(f"Error sending command: {e}")

    def send_command(self, cmd, desired_state=None):
        """Queue a command to be sent to the Arduino."""
        self.command_queue.put((cmd, desired_state))
            
    def set_finger_state(self, finger_key, desired_state):
        """Set a specific finger to a desired state (True = open, False = closed)"""
        if finger_key in self.finger_keys:
            self.send_command(finger_key, desired_state)

    def display_status(self):
        """Display the current status of all fingers."""
        print("\nHand Status:")
        for i, (name, state) in enumerate(zip(self.finger_names, self.finger_states)):
            status = "OPEN" if state else "closed"
            print(f"{name} ({self.finger_keys[i].upper()}): {status}")
        print()  # Empty line for readability

    def close(self):
        """Close the serial connection."""
        self.running = False
        if self.command_thread.is_alive():
            self.command_thread.join(timeout=1.0)
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()

def get_char():
    """Get a single character from the terminal without waiting for enter."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main():
    print("Hand Controller CLI")
    print("Controls:")
    print("Q: Thumb2 (second joint)")
    print("W: Thumb1 (first joint)")
    print("E: Index finger")
    print("R: Middle finger")
    print("T: Ring finger")
    print("Y: Pinky finger")
    print("X: Exit")
    print("\nPress any key to toggle finger position")
    
    controller = HandController()  # Will auto-detect port
    controller.display_status()  # Show initial status
    
    try:
        while True:
            char = get_char()
            if char.lower() == 'x':
                break
            if char.lower() in ['q', 'w', 'e', 'r', 't', 'y']:  # Added 'y' for pinky
                controller.send_command(char.lower())
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        controller.close()

if __name__ == "__main__":
    main()
    