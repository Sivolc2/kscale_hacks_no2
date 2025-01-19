import requests
import json
import argparse
import os

def send_test_request(json_file: str, enable_ik: bool = False):
    """Send a test request to the validation endpoint
    
    Args:
        json_file: Path to JSON file containing hand data
        enable_ik: Whether to enable IK processing
    """
    # Load the JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Send POST request to the validation endpoint
    url = 'http://localhost:5001/validate'
    headers = {
        'Content-Type': 'application/json',
        'X-Source-File': os.path.basename(json_file)
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Pretty print the response
        print("\nResponse Status:", response.status_code)
        print("\nResponse Body:")
        print(json.dumps(response.json(), indent=2))
        
        # If IK was enabled and plot was generated, print the plot path
        if enable_ik and 'validation_results' in response.json():
            for hand_key, hand_data in response.json()['validation_results'].items():
                if 'ik_results' in hand_data and 'plot_path' in hand_data['ik_results']:
                    print(f"\nPlot generated for {hand_key}:")
                    print(hand_data['ik_results']['plot_path'])
        
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response text: {e.response.text}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test the hand validation endpoint')
    parser.add_argument('--json_file', required=True, help='Path to JSON file containing hand data')
    parser.add_argument('--enable-ik', action='store_true', help='Test with IK processing enabled')
    
    args = parser.parse_args()
    send_test_request(args.json_file, enable_ik=args.enable_ik)