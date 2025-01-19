from hand_interface import RoboticHand
import argparse
import sys
import time
import glob
import serial.tools.list_ports

FINGER_MAP = {
    'thumb': ('T', "Thumb"),
    'index': ('I', "Index"),
    'middle': ('M', "Middle"),
    'ring': ('R', "Ring"),
    'pinky': ('P', "Pinky"),
    'wrist': ('W', "Wrist")
}

def find_arduino_port():
    """Find the most likely Arduino port."""
    # List all ports
    ports = list(serial.tools.list_ports.comports())
    
    # Search for common Arduino identifiers
    for port in ports:
        # Common Arduino descriptions
        if any(id in port.description.lower() for id in ['arduino', 'usb serial', 'cu.usbmodem']):
            return port.device
            
    # On MacOS, try common patterns
    if sys.platform == 'darwin':
        # Try common Mac Arduino ports
        possible_ports = glob.glob('/dev/cu.usbmodem*') + glob.glob('/dev/cu.usbserial*')
        if possible_ports:
            return possible_ports[0]
    
    # If no Arduino found, list available ports
    if ports:
        print("\nAvailable ports:")
        for port in ports:
            print(f"- {port.device}: {port.description}")
    else:
        print("\nNo serial ports found. Is the Arduino connected?")
    
    return None

def test_angle(port: str, finger: str, angle: int) -> None:
    """
    Test a specific angle for a finger.
    
    Args:
        port: Serial port for the Arduino
        finger: Which finger to move
        angle: Exact angle to test (0-180)
    """
    if finger not in FINGER_MAP:
        print(f"Invalid finger. Choose from: {', '.join(FINGER_MAP.keys())}")
        return
        
    servo_id, finger_name = FINGER_MAP[finger]
    
    try:
        with RoboticHand(port=port) as hand:
            print(f"Moving {finger_name} to {angle}°...")
            
            # Move to position
            move_func = getattr(hand, f"move_{finger}")
            success = move_func(angle)
            
            if success:
                print(f"✓ {finger_name} moved to {angle}°")
            else:
                print(f"✗ Failed to move {finger_name}")
                
    except serial.SerialException as e:
        print(f"Serial connection error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure the Arduino is connected")
        print("2. Check if the correct port is selected")
        print("3. Verify the Arduino has the correct sketch uploaded")
        
        # Try to help with port selection
        found_port = find_arduino_port()
        if found_port and found_port != port:
            print(f"\nTry using this port instead: {found_port}")
            print(f"Command: python hand_cli.py {finger} {angle} --port {found_port}")
    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(
        description='Test servo angles directly',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument('finger', choices=FINGER_MAP.keys(),
                      help='Which finger to move\n' + 
                           '\n'.join(f'  {k}: {v[1]}' for k, v in FINGER_MAP.items()))
                      
    parser.add_argument('angle', type=int,
                      help='Angle to move to (0-180)')
    
    # Try to find Arduino port first
    default_port = find_arduino_port() or '/dev/ttyUSB0'
    parser.add_argument('--port', default=default_port,
                      help=f'Serial port for Arduino (default: {default_port})')
    
    args = parser.parse_args()
    
    # Validate angle
    if not 0 <= args.angle <= 180:
        print("Error: Angle must be between 0 and 180 degrees")
        return
        
    test_angle(args.port, args.finger, args.angle)

if __name__ == "__main__":
    main()