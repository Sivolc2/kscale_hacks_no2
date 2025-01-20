from flask import Flask, request, jsonify, render_template_string, Response
from flask_cors import CORS
from hand_validator import HandValidator
from hand_ik import HandIK
from robot_control import RobotController
from sim_processor import SimProcessor
from hand_cli import HandController  # Import the HandController
import argparse
import json
import os
import time
import math
from datetime import datetime
from templates import LANDING_PAGE

app = Flask(__name__)
# Enable CORS for all domains
CORS(app)

validator = HandValidator('validation.csv')
ik_processor = HandIK(connect_robot=False)  # Don't connect to robot for IK processing
robot_controller = None  # Initialize later if robot control is enabled
sim_processor = SimProcessor()  # Initialize the simulation processor

# Initialize hand controller (will be set up in run_server)
hand_controller = None
enable_hand_updates = False  # Flag to control hand updates from VR data

# Store latest headset data
latest_headset_data = None
latest_headset_timestamp = None

def log_request(endpoint, data=None):
    """Log incoming requests with timestamp and data."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    # Only print curl data, comment out detailed request data
    if endpoint == '/control_hand':
        print(f"\n[{timestamp}] Received request to {endpoint}")
        if data:
            print(f"Request data: {json.dumps(data, indent=2)}")
    # else:
    #     print(f"\n[{timestamp}] Received request to {endpoint}")
    #     if data:
    #         print(f"Request data: {json.dumps(data, indent=2)}")

def generate_circular_motion():
    """Generate circular motion data for the robot arm."""
    radius = 20  # radius of the circle
    center_x, center_y = 0, 0  # center of the circle
    angular_speed = 1  # radians per second
    
    while True:
        current_time = time.time()
        angle = (current_time * angular_speed) % (2 * math.pi)
        
        # Calculate position on circle
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        z = 30  # constant height
        
        # Create pose data
        pose_data = {
            "pose": {
                "rightArm": {
                    "x": x,
                    "y": y,
                    "z": z
                }
            },
            "timestamp": current_time
        }
        
        yield f"data: {json.dumps(pose_data)}\n\n"
        time.sleep(0.05)  # 20Hz update rate

@app.route('/stream_motion')
def stream_motion():
    """Stream circular motion data as Server-Sent Events (SSE)."""
    return Response(
        generate_circular_motion(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )

@app.route('/')
def index():
    """Landing page with documentation"""
    return render_template_string(
        LANDING_PAGE,
        config={
            'ENABLE_IK': app.config.get('ENABLE_IK', False),
            'PLOT_IK': app.config.get('PLOT_IK', False),
            'ENABLE_ROBOT': app.config.get('ENABLE_ROBOT', False)
        }
    )

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "hand-ik-server",
        "version": "1.0.0",
        "robot_connected": robot_controller is not None
    })

@app.route('/validate', methods=['POST', 'OPTIONS'])
def validate_hands():
    # Handle preflight requests
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        return response
        
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    try:
        data = request.get_json()
        source_file = request.headers.get('X-Source-File', 'unknown')
        
        # Validate both hands
        results = {}
        for hand_key in ['left_hand', 'right_hand']:
            if hand_key in data['hands']:
                is_valid, violations = validator.validate_hand(data['hands'][hand_key])
                results[hand_key] = {
                    'is_valid': is_valid,
                    'violations': violations
                }
                
                # If IK processing is enabled, add IK results
                if app.config['ENABLE_IK']:
                    ik_results = ik_processor.process_hand(
                        data['hands'][hand_key], 
                        plot=app.config['PLOT_IK'],
                        hand_id=hand_key.split('_')[0],  # 'left' or 'right'
                        source_file=source_file
                    )
                    results[hand_key]['ik_results'] = ik_results
        
        return jsonify({
            'validation_results': results,
            'overall_valid': all(result['is_valid'] for result in results.values())
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/robot/move', methods=['POST', 'OPTIONS'])
def move_robot():
    """Direct robot control endpoint"""
    if robot_controller is None:
        return jsonify({
            "error": "Robot control is not enabled. Start server with --enable-robot flag."
        }), 400
    return robot_controller.move_robot()

@app.route('/test_simbot_move', methods=['GET'])
def test_simbot_move():
    """Test endpoint with fixed coordinates to demonstrate processing."""
    test_data = {
        "movement": {
            "rightArm": {"x": 75, "y": 30, "z": 80},  # Will be clamped
            "leftArm": {"x": -20, "y": 15}  # Missing z will get default
        }
    }
    
    result = sim_processor.process_movement(test_data["movement"])
    return jsonify({
        "input": test_data,
        "result": result
    }), 200

@app.route('/move_simbot', methods=['POST'])
def move_simbot():
    """Process movement request and return updated position."""
    log_request('/move_simbot', request.get_json() if request.is_json else None)
    
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    try:
        data = request.get_json()
        movement_data = data.get('movement', {})
        
        # Process the movement data
        result = sim_processor.process_movement(movement_data)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/get_simbot_position', methods=['GET'])
def get_simbot_position():
    """Get the current position of the simulated robot."""
    log_request('/get_simbot_position')
    
    try:
        position = sim_processor.get_current_position()
        return jsonify(position), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/get_headset_cache', methods=['GET'])
def get_headset_cache():
    """Get the last 10 headset requests and their results."""
    log_request('/get_headset_cache')
    
    try:
        cached_requests = sim_processor.get_cached_requests()
        return jsonify({
            "cache_size": len(cached_requests),
            "cached_requests": cached_requests
        }), 200
    except Exception as e:
        return jsonify({
            "error": str(e),
            "details": "Error retrieving cached requests"
        }), 400

@app.route('/move_simbot_headset', methods=['POST'])
def move_simbot_headset():
    """Process complex hand tracking data and move the simulated robot."""
    log_request('/move_simbot_headset', request.get_json() if request.is_json else None)
    
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    try:
        data = request.get_json()
        
        # Basic validation of input format
        if "hands" not in data:
            return jsonify({"error": "Missing 'hands' data"}), 400
        
        # Store the latest data with timestamp
        global latest_headset_data, latest_headset_timestamp
        latest_headset_data = data
        latest_headset_timestamp = datetime.now().isoformat()
            
        # Process the headset data
        result = sim_processor.process_headset_data(data)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "details": "Error processing headset data"
        }), 400

@app.route('/get_latest_headset_data', methods=['GET'])
def get_latest_headset_data():
    """Get the most recent headset data received by move_simbot_headset."""
    if latest_headset_data is None:
        return jsonify({
            "error": "No headset data available yet"
        }), 404
        
    return jsonify({
        "data": latest_headset_data,
        "timestamp": latest_headset_timestamp,
        "age_seconds": (datetime.now() - datetime.fromisoformat(latest_headset_timestamp)).total_seconds()
    }), 200

@app.route('/control_hand', methods=['POST'])
def control_hand():
    """Control the hand directly from headset finger state data.
    VR format: true = closed, false = open
    Expected fields: thumb, indexFinger, middleFinger, ringFinger, littleFinger"""
    log_request('/control_hand', request.get_json() if request.is_json else None)
    
    if not hand_controller:
        return jsonify({"error": "Hand controller not initialized"}), 500
        
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    try:
        data = request.get_json()
        
        # Validate input format
        if 'rightHandCurl' not in data:
            return jsonify({"error": "Missing rightHandCurl data"}), 400
        
        curl_data = data['rightHandCurl']
        required_fields = ['thumb', 'indexFinger', 'middleFinger', 'ringFinger', 'littleFinger']
        missing_fields = [field for field in required_fields if field not in curl_data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {missing_fields}"}), 400
        
        # Map VR curl data to finger commands
        # VR: true = closed, false = open
        # Arduino: true = open, false = closed (we invert the VR state)
        # Note: Thumb is reversed compared to other fingers
        finger_mapping = [
            ('q', curl_data['thumb']),           # thumb2 (pin 3) - NOT inverted because thumb is reversed
            ('w', True),                         # thumb1 (pin 5) - not controlled by VR
            ('e', curl_data['indexFinger']), # index (pin 6)
            ('r', curl_data['middleFinger']),# middle (pin 9)
            ('t', curl_data['ringFinger']),  # ring (pin 10)
            ('y', curl_data['littleFinger']) # pinky (pin 11)
        ]
        
        responses = []
        if enable_hand_updates:
            # Send commands to set each finger to desired state
            for key, desired_state in finger_mapping:
                if key == 'w':  # Skip thumb1 rotation as it's not controlled by VR
                    continue
                hand_controller.set_finger_state(key, desired_state)
                responses.append(f"Set finger {key} to {'open' if desired_state else 'closed'}")
        
        return jsonify({
            "success": True,
            "actions": responses if enable_hand_updates else [],
            "hand_updates_enabled": enable_hand_updates,
            "current_states": hand_controller.finger_states,
            "desired_states": [state for _, state in finger_mapping],
            "vr_states": curl_data  # Original VR data for debugging
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "details": "Error controlling hand"
        }), 400

@app.route('/toggle_hand_updates', methods=['POST'])
def toggle_hand_updates():
    """Toggle whether VR data updates the hand position."""
    global enable_hand_updates
    
    try:
        data = request.get_json() if request.is_json else {}
        if 'enable' in data:
            enable_hand_updates = bool(data['enable'])
        else:
            enable_hand_updates = not enable_hand_updates
            
        return jsonify({
            "success": True,
            "hand_updates_enabled": enable_hand_updates
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "details": "Error toggling hand updates"
        }), 400

def run_server(enable_ik: bool = False, plot_ik: bool = False, 
              enable_robot: bool = False, robot_ip: str = '192.168.42.1',
              port: int = 5001, host: str = '0.0.0.0', ssl_context=None,
              hand_port: str = None, enable_updates: bool = False):
    """Run the Flask server"""
    app.config['ENABLE_IK'] = enable_ik
    app.config['PLOT_IK'] = plot_ik
    app.config['ENABLE_ROBOT'] = enable_robot
    
    global enable_hand_updates
    enable_hand_updates = enable_updates
    
    # Initialize robot controller if enabled
    global robot_controller
    if enable_robot:
        try:
            robot_controller = RobotController(robot_ip)
            print(f"Robot control enabled, connected to {robot_ip}")
        except Exception as e:
            print(f"Warning: Failed to connect to robot at {robot_ip}: {e}")
            print("Robot control will be disabled")
    
    # Initialize hand controller if port specified
    global hand_controller
    if hand_port:
        try:
            hand_controller = HandController(port=hand_port)
            print(f"Hand controller enabled, connected to {hand_port}")
        except Exception as e:
            print(f"Warning: Failed to connect to hand on {hand_port}: {e}")
            print("Hand control will be disabled")
    
    # Print server info
    protocol = "https" if ssl_context else "http"
    print(f"\nStarting Hand IK Server:")
    print(f"========================")
    print(f"URL: {protocol}://{host}:{port}")
    print(f"IK Processing: {'Enabled' if enable_ik else 'Disabled'}")
    print(f"IK Plotting: {'Enabled' if plot_ik else 'Disabled'}")
    print(f"Robot Control: {'Enabled' if robot_controller else 'Disabled'}")
    print("\nEndpoints:")
    print(f"- GET {protocol}://{host}:{port} : Documentation")
    print(f"- GET {protocol}://{host}:{port}/health : Health check")
    print(f"- POST {protocol}://{host}:{port}/validate : Hand validation and IK processing")
    if robot_controller:
        print(f"- POST {protocol}://{host}:{port}/robot/move : Direct robot control")
    print("\nPress Ctrl+C to stop the server")
    
    app.run(
        host=host,
        port=port,
        ssl_context=ssl_context
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Hand validation and IK processing server')
    parser.add_argument('--enable-ik', action='store_true', help='Enable inverse kinematics processing')
    parser.add_argument('--plot-ik', action='store_true', help='Plot IK results (requires --enable-ik)')
    parser.add_argument('--enable-robot', action='store_true', help='Enable robot control')
    parser.add_argument('--robot-ip', default='192.168.42.1', help='Robot IP address')
    parser.add_argument('--port', type=int, default=5001, help='Port to run the server on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--ssl-cert', help='Path to SSL certificate file')
    parser.add_argument('--ssl-key', help='Path to SSL private key file')
    parser.add_argument('--hand-port', help='Serial port for hand controller')
    parser.add_argument('--enable-hand-updates', action='store_true', 
                       help='Enable hand position updates from VR data')
    
    args = parser.parse_args()
    
    if args.plot_ik and not args.enable_ik:
        parser.error("--plot-ik requires --enable-ik to be set")
    
    # Configure SSL if certificates provided
    ssl_context = None
    if args.ssl_cert and args.ssl_key:
        ssl_context = (args.ssl_cert, args.ssl_key)
    
    run_server(
        enable_ik=args.enable_ik,
        plot_ik=args.plot_ik,
        enable_robot=args.enable_robot,
        robot_ip=args.robot_ip,
        port=args.port,
        host=args.host,
        ssl_context=ssl_context,
        hand_port=args.hand_port,
        enable_updates=args.enable_hand_updates
    )
