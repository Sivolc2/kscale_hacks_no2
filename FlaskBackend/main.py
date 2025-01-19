from flask import Flask, request, jsonify
from hand_validator import HandValidator
from hand_ik import HandIK
import argparse
import json
import os

app = Flask(__name__)
validator = HandValidator('validation.csv')
ik_processor = HandIK()

@app.route('/validate', methods=['POST'])
def validate_hands():
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

def run_server(enable_ik: bool = False, plot_ik: bool = False):
    app.config['ENABLE_IK'] = enable_ik
    app.config['PLOT_IK'] = plot_ik
    app.run(host='0.0.0.0', port=5001)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Hand validation and IK processing server')
    parser.add_argument('--enable-ik', action='store_true', help='Enable inverse kinematics processing')
    parser.add_argument('--plot-ik', action='store_true', help='Plot IK results (requires --enable-ik)')
    
    args = parser.parse_args()
    
    if args.plot_ik and not args.enable_ik:
        parser.error("--plot-ik requires --enable-ik to be set")
    
    run_server(enable_ik=args.enable_ik, plot_ik=args.plot_ik)
