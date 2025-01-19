from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from hand_validator import HandValidator
from hand_ik import HandIK
import argparse
import json
import os
from templates import LANDING_PAGE

app = Flask(__name__)
# Enable CORS for all domains
CORS(app)

validator = HandValidator('validation.csv')
ik_processor = HandIK()

@app.route('/')
def index():
    """Landing page with documentation"""
    return render_template_string(
        LANDING_PAGE,
        config={
            'ENABLE_IK': app.config.get('ENABLE_IK', False),
            'PLOT_IK': app.config.get('PLOT_IK', False)
        }
    )

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "hand-ik-server",
        "version": "1.0.0"
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

def run_server(enable_ik: bool = False, plot_ik: bool = False, port: int = 5001, host: str = '0.0.0.0', ssl_context=None):
    """Run the Flask server"""
    app.config['ENABLE_IK'] = enable_ik
    app.config['PLOT_IK'] = plot_ik
    
    # Print server info
    protocol = "https" if ssl_context else "http"
    print(f"\nStarting Hand IK Server:")
    print(f"========================")
    print(f"URL: {protocol}://{host}:{port}")
    print(f"IK Processing: {'Enabled' if enable_ik else 'Disabled'}")
    print(f"IK Plotting: {'Enabled' if plot_ik else 'Disabled'}")
    print("\nEndpoints:")
    print(f"- GET {protocol}://{host}:{port} : Documentation")
    print(f"- GET {protocol}://{host}:{port}/health : Health check")
    print(f"- POST {protocol}://{host}:{port}/validate : Hand validation and IK processing")
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
        port=args.port,
        host=args.host,
        ssl_context=ssl_context
    )
