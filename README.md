# Project HandVision 🤖👋
> Hack the Future of Robot Control

## Overview
Project HandVision enables natural robot control through Vision Pro hand tracking, featuring a custom Arduino robotic hand and simulated Unitree G1 humanoid control.

### Technology Stack
- **Vision Pro** for hand tracking
- **Custom Arduino Robotic Hand** 
- **MujocoWASM** for humanoid simulation
- **Three.js** for visualization
- **Next.js** frontend
- **Flask** backend

## Quick Start

### Environment Setup
```bash
python -v 
3.11.7

python -m venv backend_env
source backend_env/bin/activate
pip install -r requirements.txt
```

### Server Configuration Options

## Run streaming from the backend

#### Basic Setup (Hand Control Only)
```bash
# Start backend listening for headset updates
python FlaskBackend/main.py --hand-port /dev/cu.usbmodem* --port 5005 --enable-hand-updates
```

Toggle listening for movement events in the app
```bash
curl -X POST http://localhost:5005/toggle_hand_updates
```

Manual control using keyboard:
```bash
python FlaskBackend/hand_cli.py
```

#### Full Robot Control Setup
```bash
python FlaskBackend/main.py --port 5005 --host 0.0.0.0 --enable-ik --enable-robot --robot-ip 192.168.42.1
```


### Network Configuration

#### Server Address
- Local access: Use `127.0.0.1` or `localhost`
- Remote access: Use machine's IP (e.g., `192.168.154.196`)
- Port specified by `--port` argument (default: 5005)

#### Robot Network Setup
1. Robot creates WiFi network (IP: 192.168.42.1)
2. Connect computer to robot's network
3. Verify: `ping 192.168.42.1`
4. Start server with robot control

### API Endpoints
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/` | GET | Documentation page |
| `/health` | GET | Server health check |
| `/validate` | POST | Hand validation and IK |
| `/robot/move` | POST | Robot control |
| `/control_hand` | POST | Direct hand control |

## Robot Control Examples

### REST API Usage
```bash
# Move robot joints
curl -X POST http://localhost:5005/robot/move \
  -H "Content-Type: application/json" \
  -d '{
    "joints": [
      {"id": 13, "position": 0.5},  # wrist
      {"id": 14, "position": 0.0}   # pincer
    ]
  }'
```

### Python Implementation
```python
import requests

def move_robot(wrist_pos: float, pincer_pos: float):
    response = requests.post(
        'http://localhost:5005/robot/move',
        json={
            'joints': [
                {'id': 13, 'position': wrist_pos},
                {'id': 14, 'position': pincer_pos}
            ]
        }
    )
    return response.json()
```

## Troubleshooting

### Connection Issues
```bash
# Test robot connectivity
ping 192.168.42.1
nc -vz 192.168.42.1 50051

# Verify server health
curl http://localhost:5005/health
```

### Common Errors
1. **405 Method Not Allowed**: Ensure correct HTTP method
2. **400 Bad Request**: Check JSON format and Content-Type header
3. **Connection Refused**: Verify network configuration

## Future Development
- Force feedback implementation
- Multi-hand tracking support
- Complex manipulation tasks
- Vision system integration

## Team
Built with ❤️ by Nathan, Clovis, Gary, Aiden, Daniel, Josh during KHacks-3.0

## License
[Add License Information]