# kscale_hacks_no2

## Server Setup

### Start server without robot control
```bash
python FlaskBackend/main.py --port 5005 --host 0.0.0.0 --enable-ik
```

### Start server with robot control
```bash
python FlaskBackend/main.py --port 5005 --host 0.0.0.0 --enable-ik --enable-robot --robot-ip 192.168.42.1
```

### IP Address Configuration

1. **Server Address**:
   - When server starts, it shows available addresses:
     ```
     Running on http://127.0.0.1:5005
     Running on http://192.168.154.196:5005
     ```
   - Use `127.0.0.1` or `localhost` when accessing from the same machine
   - Use the machine's IP (e.g., `192.168.154.196`) when accessing from other devices
   - Port is specified by `--port` argument (5005 in examples)

2. **Robot IP**:
   - Default robot IP is `192.168.42.1` with port 50051
   - Use `--robot-ip` to specify a different address
   - Make sure your machine is on the same network as the robot
   - Robot must be powered on and running KOS server

### Network Setup
1. **Robot Network**:
   - Robot creates its own WiFi network (default IP: 192.168.42.1)
   - Connect your computer to the robot's WiFi network
   - Or connect both robot and computer to same network

2. **Connection Order**:
   1. Power on robot and wait for boot
   2. Connect to robot's WiFi network
   3. Verify connection: `ping 192.168.42.1`
   4. Start server with robot control

### Connectivity Troubleshooting
1. Check robot connection:
   ```bash
   # Check if robot is reachable
   ping 192.168.42.1
   
   # Check if KOS port is open (requires netcat)
   nc -vz 192.168.42.1 50051
   ```

2. Verify server is accessible:
   ```bash
   curl http://localhost:5005/health
   ```

3. Common issues:
   - Wrong network configuration
     - Make sure you're connected to robot's WiFi
     - Or both devices are on same network
   - Robot not ready
     - Power cycle the robot
     - Wait for full boot sequence
   - Server issues
     - Check server logs for connection errors
     - Restart server after fixing network
   - Wrong port/protocol
     - Robot uses port 50051 for KOS
     - Server uses port 5005 for HTTP

4. Debug sequence:
   ```bash
   # 1. Check network connection
   ping 192.168.42.1
   
   # 2. If ping works, check KOS port
   nc -vz 192.168.42.1 50051
   
   # 3. Start server with debug output
   python FlaskBackend/main.py --port 5005 --host 0.0.0.0 --enable-ik --enable-robot --robot-ip 192.168.42.1
   
   # 4. Test robot control
   curl -X POST http://localhost:5005/robot/move \
     -H "Content-Type: application/json" \
     -d '{"joints": [{"id": 13, "position": 0.5}]}'
   ```

## Robot Control Examples

### Using test_movement.py directly
```python
# Basic movement test
python robot_commands/test_movement.py

# Configure and move specific joints
from pykos import KOS

client = KOS(ip='192.168.42.1')

# Configure wrist and pincer
client.actuator.configure_actuator(actuator_id=13, torque_enabled=True)  # wrist
client.actuator.configure_actuator(actuator_id=14, torque_enabled=True)  # pincer

# Move joints
commands = [
    {"actuator_id": 13, "position": 0.5},  # wrist at middle position
    {"actuator_id": 14, "position": 0.0}   # pincer closed
]
response = client.actuator.command_actuators(commands)
```

### Using the REST API endpoint
```bash
# Move wrist and pincer using curl
curl -X POST http://localhost:5005/robot/move \
  -H "Content-Type: application/json" \
  -d '{
    "joints": [
      {"id": 13, "position": 0.5},
      {"id": 14, "position": 0.0}
    ]
  }'

# Example Python request
import requests

def move_robot(wrist_pos: float, pincer_pos: float):
    response = requests.post(
        'http://localhost:5005/robot/move',
        json={
            'joints': [
                {'id': 13, 'position': wrist_pos},   # wrist
                {'id': 14, 'position': pincer_pos}   # pincer
            ]
        }
    )
    return response.json()

# Example usage
move_robot(wrist_pos=0.5, pincer_pos=0.0)  # Center wrist, close pincer
move_robot(wrist_pos=1.0, pincer_pos=1.0)  # Full right, open pincer
```

## Environment Setup
```bash
python 3.11.7
pip install -r requirements.txt
```

### API Endpoints and Methods
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/` | GET | Documentation page |
| `/health` | GET | Server health check |
| `/validate` | POST | Hand validation and IK |
| `/robot/move` | POST | Robot control (requires --enable-robot) |

### Common Errors
1. **405 Method Not Allowed**
   ```bash
   # Wrong: Using GET method
   curl http://localhost:5005/robot/move           # This will fail
   
   # Correct: Using POST method with -X POST
   curl -X POST http://localhost:5005/robot/move \
     -H "Content-Type: application/json" \
     -d '{
       "joints": [
         {"id": 13, "position": 0.5},
         {"id": 14, "position": 0.0}
       ]
     }'
   ```

2. **400 Bad Request**
   ```bash
   # Wrong: Missing Content-Type header
   curl -X POST http://localhost:5005/robot/move \
     -d '{"joints": [...]}'
   
   # Wrong: Invalid JSON format
   curl -X POST http://localhost:5005/robot/move \
     -H "Content-Type: application/json" \
     -d 'not valid json'
   
   # Correct: Proper headers and JSON
   curl -X POST http://localhost:5005/robot/move \
     -H "Content-Type: application/json" \
     -d '{"joints": [{"id": 13, "position": 0.5}]}'
   ```

### Testing the API
1. Check server health:
   ```bash
   curl http://localhost:5005/health
   ```

2. Test robot movement:
   ```