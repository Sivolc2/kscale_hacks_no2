#!/usr/bin/env python3
import requests
import time
import json
import sys

def test_finger_movement(base_url="http://localhost:5005"):
    """Test individual finger movements through the API."""
    
    # First enable hand updates
    print("\nEnabling hand updates...")
    response = requests.post(f"{base_url}/toggle_hand_updates", json={"enable": True})
    if not response.ok:
        print("Failed to enable hand updates!")
        return False

    # Test each finger individually
    fingers = [
        ("Thumb2", {"thumb": True, "indexFinger": False, "middleFinger": False, "ringFinger": False, "littleFinger": False}),
        ("Index", {"thumb": False, "indexFinger": True, "middleFinger": False, "ringFinger": False, "littleFinger": False}),
        ("Middle", {"thumb": False, "indexFinger": False, "middleFinger": True, "ringFinger": False, "littleFinger": False}),
        ("Ring", {"thumb": False, "indexFinger": False, "middleFinger": False, "ringFinger": True, "littleFinger": False}),
        ("Pinky", {"thumb": False, "indexFinger": False, "middleFinger": False, "ringFinger": False, "littleFinger": True})
    ]

    print("\nTesting individual finger movements...")
    for finger_name, curl_state in fingers:
        print(f"\nTesting {finger_name}...")
        
        # Close the finger
        response = requests.post(
            f"{base_url}/control_hand",
            json={"rightHandCurl": curl_state}
        )
        
        if response.ok:
            result = response.json()
            print(f"Close {finger_name} response: {json.dumps(result, indent=2)}")
        else:
            print(f"Failed to close {finger_name}: {response.status_code}")
            return False
            
        time.sleep(1)  # Wait for movement to complete
        
        # Open the finger (invert all states)
        open_state = {k: not v for k, v in curl_state.items()}
        response = requests.post(
            f"{base_url}/control_hand",
            json={"rightHandCurl": open_state}
        )
        
        if response.ok:
            result = response.json()
            print(f"Open {finger_name} response: {json.dumps(result, indent=2)}")
        else:
            print(f"Failed to open {finger_name}: {response.status_code}")
            return False
            
        time.sleep(1)  # Wait for movement to complete

    # Test all fingers together
    print("\nTesting all fingers together...")
    
    # Close all fingers
    all_closed = {"thumb": True, "indexFinger": True, "middleFinger": True, "ringFinger": True, "littleFinger": True}
    response = requests.post(
        f"{base_url}/control_hand",
        json={"rightHandCurl": all_closed}
    )
    
    if response.ok:
        result = response.json()
        print(f"Close all response: {json.dumps(result, indent=2)}")
    else:
        print(f"Failed to close all fingers: {response.status_code}")
        return False
        
    time.sleep(2)  # Wait for movement to complete
    
    # Open all fingers
    all_open = {"thumb": False, "indexFinger": False, "middleFinger": False, "ringFinger": False, "littleFinger": False}
    response = requests.post(
        f"{base_url}/control_hand",
        json={"rightHandCurl": all_open}
    )
    
    if response.ok:
        result = response.json()
        print(f"Open all response: {json.dumps(result, indent=2)}")
    else:
        print(f"Failed to open all fingers: {response.status_code}")
        return False

    print("\nAll tests completed successfully!")
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test robotic hand finger movements')
    parser.add_argument('--url', default='http://localhost:5005', help='Base URL of the Flask server')
    
    args = parser.parse_args()
    
    try:
        test_finger_movement(args.url)
    except requests.exceptions.ConnectionError:
        print(f"\nError: Could not connect to server at {args.url}")
        print("Make sure the Flask server is running and the URL is correct.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        sys.exit(0)
