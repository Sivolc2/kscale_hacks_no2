import requests
import json
import time
import math

# Configuration
BACKEND_URL = 'http://192.168.154.196:5005'
ENDPOINT = f'{BACKEND_URL}/move_simbot_headset'

def generate_hand_movement(t, is_left=True):
    """Generate circular hand movement data.
    
    Args:
        t (float): Time parameter (0 to 2π)
        is_left (bool): Whether to generate left or right hand data
    
    Returns:
        list: List of hand points with positions
    """
    # Base radius for the circular motion
    radius = 0.3
    
    # Center position, different for left and right hands
    center_x = -0.3 if is_left else 0.3
    
    # Calculate basic circular motion
    x = center_x + radius * math.cos(t)
    y = radius * math.sin(t)
    z = 0.5  # Constant height
    
    # Generate all hand points based on the wrist position
    points = []
    point_names = [
        "handWrist", "handThumbKnuckle", "handThumbIntermediateBase",
        "handThumbIntermediateTip", "handThumbTip", "handIndexFingerMetacarpal",
        "handIndexFingerKnuckle", "handIndexFingerIntermediateBase",
        "handIndexFingerIntermediateTip", "handIndexFingerTip"
    ]
    
    for i, name in enumerate(point_names):
        # Add small offsets for different points relative to wrist
        offset_x = i * 0.02
        offset_y = i * 0.01
        offset_z = i * 0.01
        
        points.append({
            "id": i,
            "name": name,
            "x": x + offset_x,
            "y": y + offset_y,
            "z": z + offset_z
        })
    
    return points

def send_movement(hand_data):
    """Send hand tracking data to the backend and print response."""
    try:
        print("\nSending hand data:", json.dumps(hand_data, indent=2))
        
        response = requests.post(
            ENDPOINT,
            json=hand_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print("Response status:", response.status_code)
        print("Response data:", json.dumps(response.json(), indent=2))
        
        return response.status_code == 200
        
    except Exception as e:
        print("Error sending movement:", e)
        return False

def main():
    print(f"Starting headset movement test sequence to {ENDPOINT}")
    
    # Generate a sequence of movements
    num_steps = 50
    for i in range(num_steps):
        t = (i / num_steps) * 2 * math.pi  # Time parameter from 0 to 2π
        
        # Generate hand data
        hand_data = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "hands": {
                "left_hand": {
                    "points": generate_hand_movement(t, is_left=True)
                },
                "right_hand": {
                    "points": generate_hand_movement(t, is_left=False)
                }
            }
        }
        
        print(f"\n=== Movement {i+1} of {num_steps} ===")
        
        if send_movement(hand_data):
            print(f"Successfully sent movement {i+1}")
        else:
            print(f"Failed to send movement {i+1}")
            break
            
        # Wait a bit between movements
        time.sleep(0.1)
    
    print("\nTest sequence completed!")

if __name__ == "__main__":
    main() 