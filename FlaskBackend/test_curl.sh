#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Testing Hand IK Server${NC}"
echo "====================="

# Test health endpoint
echo -e "\n${GREEN}1. Testing Health Endpoint${NC}"
curl -X GET http://http://192.168.154.196/:5001/health

# Test validation with inline JSON
echo -e "\n\n${GREEN}2. Testing Validation (Basic)${NC}"
curl -X POST http://http://192.168.154.196/:5001/validate \
    -H "Content-Type: application/json" \
    -d '{
    "hands": {
        "left_hand": {
            "points": [
                {"id": 0, "name": "handWrist", "x": 0.1, "y": 0.2, "z": 0.3},
                {"id": 4, "name": "handThumbTip", "x": 0.3, "y": 0.4, "z": 0.5},
                {"id": 9, "name": "handIndexFingerTip", "x": 0.55, "y": 0.65, "z": 0.75},
                {"id": 14, "name": "handMiddleFingerTip", "x": 0.8, "y": 0.9, "z": 1.0},
                {"id": 19, "name": "handRingFingerTip", "x": 1.05, "y": 1.15, "z": 1.25},
                {"id": 24, "name": "handLittleFingerTip", "x": 1.3, "y": 1.4, "z": 1.5}
            ]
        }
    }
}'

# Test validation with file
if [ -f "example.json" ]; then
    echo -e "\n\n${GREEN}3. Testing Validation (File Input)${NC}"
    curl -X POST http://http://192.168.154.196/:5001/validate \
        -H "Content-Type: application/json" \
        -H "X-Source-File: example.json" \
        -d @example.json
else
    echo -e "\n\n${GREEN}3. Skipping File Test (example.json not found)${NC}"
fi

echo -e "\n\nDone!" 