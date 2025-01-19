from flask import Flask, request, jsonify
from hand_validator import HandValidator
import os

app = Flask(__name__)
validator = HandValidator('sample_ruleset.csv')

@app.route('/validate', methods=['POST'])
def validate_hands():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    try:
        data = request.get_json()
        
        # Validate both hands
        results = {}
        for hand_key in ['left_hand', 'right_hand']:
            if hand_key in data['hands']:
                is_valid, violations = validator.validate_hand(data['hands'][hand_key])
                results[hand_key] = {
                    'is_valid': is_valid,
                    'violations': violations
                }
        
        return jsonify({
            'validation_results': results,
            'overall_valid': all(result['is_valid'] for result in results.values())
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def run_server():
    app.run(host='0.0.0.0', port=5001)

if __name__ == '__main__':
    run_server()
