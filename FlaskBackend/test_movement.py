import requests
import json
import time

# Configuration
BACKEND_URL = 'http://192.168.154.196:5005'  # Update this to match your backend URL
ENDPOINT = f'{BACKEND_URL}/move_simbot'

# Test coordinates - three different positions
test_positions = [
    {
        # Position 1: Arms spread out
        "movement": {
            "rightArm": {"x": 45, "y": 0, "z": 30},
            "leftArm": {"x": -45, "y": 0, "z": 30}
        }
    },
    {
        # Position 2: Arms forward
        "movement": {
            "rightArm": {"x": 0, "y": 45, "z": 40},
            "leftArm": {"x": 0, "y": 45, "z": 40}
        }
    },
    {
        # Position 3: Arms up and apart
        "movement": {
            "rightArm": {"x": 30, "y": 20, "z": 55},
            "leftArm": {"x": -30, "y": 20, "z": 55}
        }
    }
]

def send_movement(position_data):
    """Send movement data to the backend and print response."""
    try:
        print("\nSending position:", json.dumps(position_data, indent=2))
        
        response = requests.post(
            ENDPOINT,
            json=position_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print("Response status:", response.status_code)
        print("Response data:", json.dumps(response.json(), indent=2))
        
        return response.status_code == 200
        
    except Exception as e:
        print("Error sending movement:", e)
        return False

def main():
    print(f"Starting movement test sequence to {ENDPOINT}")
    
    for i, position in enumerate(test_positions, 1):
        print(f"\n=== Position {i} of {len(test_positions)} ===")
        
        if send_movement(position):
            print(f"Successfully sent position {i}")
        else:
            print(f"Failed to send position {i}")
            
        # Wait 2 seconds between movements to see the animation
        if i < len(test_positions):
            print("Waiting 2 seconds before next movement...")
            time.sleep(2)
    
    print("\nTest sequence completed!")

if __name__ == "__main__":
    main() 