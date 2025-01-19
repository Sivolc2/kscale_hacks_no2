import requests
import json
import time
import math

# Configuration
BACKEND_URL = 'http://192.168.154.196:5005'
ENDPOINT = f'{BACKEND_URL}/move_simbot_headset'
CACHE_ENDPOINT = f'{BACKEND_URL}/get_headset_cache'

def check_cache():
    """Get and print the current cache contents."""
    try:
        response = requests.get(CACHE_ENDPOINT)
        if response.status_code == 200:
            cache_data = response.json()
            print("\nCache contents:")
            print(f"Cache size: {cache_data['cache_size']}")
            for i, entry in enumerate(cache_data['cached_requests'], 1):
                print(f"\nEntry {i}:")
                print(f"Timestamp: {entry['timestamp']}")
                print(f"Result pose: {json.dumps(entry['result']['pose'], indent=2)}")
                if 'debug' in entry['result']:
                    print("Transformations:")
                    print(f"Scaling: {json.dumps(entry['result']['debug']['scaling_factors'], indent=2)}")
                    print(f"Offsets: {json.dumps(entry['result']['debug']['offsets'], indent=2)}")
        else:
            print("Failed to retrieve cache:", response.status_code)
    except Exception as e:
        print("Error checking cache:", e)

def generate_hand_movement(t, is_left=True):
    """Generate hand movement data that matches real headset ranges.
    
    Args:
        t (float): Time parameter (0 to 2π)
        is_left (bool): Whether to generate left or right hand data
    
    Returns:
        list: List of hand points with positions
    """
    # Base radius and ranges matching real headset data
    radius = 0.15  # Smaller radius to match real movement range
    
    # Center position, different for left and right hands
    # x: -0.3 to 0.3
    # y: 0.8 to 1.3
    # z: -0.3 to -0.05
    center_x = -0.2 if is_left else 0.2
    center_y = 1.0  # Base height
    center_z = -0.2  # Base depth
    
    # Calculate basic circular motion
    x = center_x + radius * math.cos(t)
    y = center_y + radius * math.sin(t)
    z = center_z + radius * math.cos(t * 2) * 0.1  # Smaller z movement
    
    # Generate all hand points based on the wrist position
    points = []
    point_names = [
        "wrist", "forearmWrist", "forearmArm",
        "thumbKnuckle", "thumbIntermediateBase", "thumbIntermediateTip", "thumbTip",
        "indexFingerMetacarpal", "indexFingerKnuckle", "indexFingerIntermediateBase",
        "indexFingerIntermediateTip", "indexFingerTip",
        "middleFingerMetacarpal", "middleFingerKnuckle", "middleFingerIntermediateBase",
        "middleFingerIntermediateTip", "middleFingerTip",
        "ringFingerMetacarpal", "ringFingerKnuckle", "ringFingerIntermediateBase",
        "ringFingerIntermediateTip", "ringFingerTip",
        "littleFingerMetacarpal", "littleFingerKnuckle", "littleFingerIntermediateBase",
        "littleFingerIntermediateTip", "littleFingerTip"
    ]
    
    for i, name in enumerate(point_names):
        # Add small offsets for different points relative to wrist
        # Finger points are further from wrist
        is_finger_tip = "Tip" in name
        is_finger_base = "Knuckle" in name or "Metacarpal" in name
        
        offset_x = (i % 5) * 0.01 * (1.5 if is_finger_tip else 1.0)
        offset_y = (i % 3) * 0.02 * (2.0 if is_finger_tip else 1.0)
        offset_z = (i % 4) * 0.01 * (1.5 if is_finger_tip else 1.0)
        
        if is_finger_base:
            offset_y *= 0.5  # Bases closer to wrist
        
        points.append({
            "id": name,  # Using name as ID to match real data
            "name": name,
            "x": x + (offset_x if is_left else -offset_x),
            "y": y + offset_y,
            "z": z + offset_z
        })
    
    return points

def send_movement(hand_data):
    """Send hand tracking data to the backend and print response."""
    try:
        print("\nSending hand data for positions:")
        for hand_key, hand in hand_data["hands"].items():
            wrist = next((p for p in hand["points"] if p["name"] == "wrist"), None)
            index_tip = next((p for p in hand["points"] if p["name"] == "indexFingerTip"), None)
            if wrist:
                print(f"\n{hand_key} wrist: x={wrist['x']:.3f}, y={wrist['y']:.3f}, z={wrist['z']:.3f}")
            if index_tip:
                print(f"{hand_key} index tip: x={index_tip['x']:.3f}, y={index_tip['y']:.3f}, z={index_tip['z']:.3f}")
        
        response = requests.post(
            ENDPOINT,
            json=hand_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print("\nResponse status:", response.status_code)
        result = response.json()
        print("Processed positions:")
        for arm_key, pos in result["pose"].items():
            print(f"{arm_key}: x={pos['x']:.1f}, y={pos['y']:.1f}, z={pos['z']:.1f}")
        
        return response.status_code == 200
        
    except Exception as e:
        print("Error sending movement:", e)
        return False

def main():
    print(f"Starting headset movement test sequence to {ENDPOINT}")
    print("Movement ranges:")
    print("- X: -0.3 to 0.3 (width)")
    print("- Y: 0.8 to 1.3 (height)")
    print("- Z: -0.3 to -0.05 (depth)")
    
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
            # Check cache every 10 movements
            if (i + 1) % 10 == 0:
                check_cache()
        else:
            print(f"Failed to send movement {i+1}")
            break
            
        # Wait a bit between movements
        time.sleep(0.1)
    
    print("\nTest sequence completed!")
    print("\nFinal cache state:")
    check_cache()

if __name__ == "__main__":
    main() 