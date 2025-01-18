from flask import Flask, request, jsonify
import time

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_json():
    if request.is_json:
        data = request.get_json()
        # Process the JSON data here
        print(data)
        return jsonify({"message": "JSON received"}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400

def run_server():
    app.run(host='0.0.0.0', port=5001)

if __name__ == '__main__':
    run_server()