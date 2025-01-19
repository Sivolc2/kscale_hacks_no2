import requests
import json
from pprint import pprint

def test_hand_validation():
    url = "http://localhost:5001/validate"
    headers = {"Content-Type": "application/json"}

    # Test case 1: Valid hand configuration with legal angles
    valid_data = {
        "timestamp": "2025-01-18T18:30:00Z",
        "hands": {
            "left_hand": {
                "points": [
                    {"id": 0, "name": "handWrist", "x": 0, "y": 0, "z": 0},
                    {"id": 1, "name": "handThumbKnuckle", "x": 1, "y": 0, "z": 0},
                    {"id": 2, "name": "handThumbIntermediateBase", "x": 1.8, "y": 0.2, "z": 0},  # ~15° angle
                    {"id": 3, "name": "handThumbIntermediateTip", "x": 2.5, "y": 0.4, "z": 0},   # ~20° angle
                    {"id": 4, "name": "handThumbTip", "x": 3.0, "y": 0.8, "z": 0}                # ~30° angle
                ]
            }
        }
    }

    # Test case 2: Invalid hand configuration (extreme angles)
    invalid_data = {
        "timestamp": "2025-01-18T18:30:00Z",
        "hands": {
            "left_hand": {
                "points": [
                    {"id": 0, "name": "handWrist", "x": 0, "y": 0, "z": 0},
                    {"id": 1, "name": "handThumbKnuckle", "x": 1, "y": 0, "z": 0},
                    {"id": 2, "name": "handThumbIntermediateBase", "x": 2, "y": 2, "z": 0},      # ~90° angle
                    {"id": 3, "name": "handThumbIntermediateTip", "x": 3, "y": 4, "z": 0},       # ~90° angle
                    {"id": 4, "name": "handThumbTip", "x": 4, "y": 6, "z": 0}                    # ~90° angle
                ]
            }
        }
    }

    print("\nTesting valid hand configuration:")
    try:
        response = requests.post(url, headers=headers, json=valid_data)
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure the Flask app is running.")

    print("\nTesting invalid hand configuration:")
    try:
        response = requests.post(url, headers=headers, json=invalid_data)
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure the Flask app is running.")

if __name__ == "__main__":
    test_hand_validation() 