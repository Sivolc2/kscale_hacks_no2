from flask import Flask, request, jsonify, render_template_string, Response
from flask_cors import CORS
from hand_validator import HandValidator
from hand_ik import HandIK
from robot_control import RobotController
from sim_processor import SimProcessor
import argparse
import json
import os
import time
import math
from templates import LANDING_PAGE

app = Flask(__name__)
# Enable CORS for all domains
CORS(app)

validator = HandValidator('validation.csv')
ik_processor = HandIK(connect_robot=False)  # Don't connect to robot for IK processing
robot_controller = None  # Initialize later if robot control is enabled
sim_processor = SimProcessor()  # Initialize the simulation processor

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
    try:
        position = sim_processor.get_current_position()
        return jsonify(position), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/move_simbot_headset', methods=['POST'])
def move_simbot_headset():
    """Process complex hand tracking data and move the simulated robot.
    
    Expects data in the format:
    {
        "timestamp": "2025-01-18T18:30:00Z",
        "hands": {
            "left_hand": {
                "points": [
                    {"id": 0, "name": "handWrist", "x": 0.1, "y": 0.2, "z": 0.3},
                    ...
                ]
            },
            "right_hand": {
                "points": [
                    {"id": 0, "name": "handWrist", "x": 0.1, "y": 0.2, "z": 0.3},
                    ...
                ]
            }
        }
    }
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    try:
        data = request.get_json()
        
        # Basic validation of input format
        if "hands" not in data:
            return jsonify({"error": "Missing 'hands' data"}), 400
            
        # Process the headset data
        result = sim_processor.process_headset_data(data)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "details": "Error processing headset data"
        }), 400

def run_server(enable_ik: bool = False, plot_ik: bool = False, 
              enable_robot: bool = False, robot_ip: str = '192.168.42.1',
              port: int = 5001, host: str = '0.0.0.0', ssl_context=None):
    """Run the Flask server"""
    app.config['ENABLE_IK'] = enable_ik
    app.config['PLOT_IK'] = plot_ik
    app.config['ENABLE_ROBOT'] = enable_robot
    
    # Initialize robot controller if enabled
    global robot_controller
    if enable_robot:
        try:
            robot_controller = RobotController(robot_ip)
            print(f"Robot control enabled, connected to {robot_ip}")
        except Exception as e:
            print(f"Warning: Failed to connect to robot at {robot_ip}: {e}")
            print("Robot control will be disabled")
    
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
        ssl_context=ssl_context
    )
