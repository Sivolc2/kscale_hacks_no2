# Hand Inverse Kinematics System

This system performs inverse kinematics (IK) calculations on hand data to determine joint angles that would achieve the observed finger positions.

## System Overview

### 1. Kinematic Chain Structure
Each finger is modeled as a kinematic chain with the following joints:

#### Thumb Chain
- Base (Origin)
- Knuckle (3 DOF: rotation in all axes [x,y,z])
- Intermediate (1 DOF: bend only [y])
- Tip (1 DOF: bend only [y])
- Length: 4cm total (2cm + 2cm segments)

#### Other Fingers (Index, Middle, Ring, Little)
- Base (Origin)
- Knuckle (2 DOF: flexion and abduction [x,y])
- Intermediate (1 DOF: bend only [y])
- Tip (1 DOF: bend only [y])
- Length: 5cm total (3cm + 2cm segments)

### 2. Input Format
The system accepts hand data in JSON format:
```json
{
  "hands": {
    "left_hand": {
      "points": [
        {"name": "handThumbKnuckle", "x": 0.15, "y": 0.25, "z": 0.35},
        {"name": "handThumbTip", "x": 0.3, "y": 0.4, "z": 0.5},
        // ... other points
      ]
    },
    "right_hand": {
      // Similar structure
    }
  }
}
```

### 3. Output Explanation
The system returns:

```json
{
  "validation_results": {
    "left_hand": {
      "ik_results": {
        "thumb": [0.0, -2.98, 0.85, 0.0],  // Joint angles in radians
        "index": [0.0, 0.0, 0.0, 0.0],     // [base, knuckle, intermediate, tip]
        "middle": [0.0, 0.0, 0.0, 0.0],
        "ring": [0.0, 0.0, 0.0, 0.0],
        "little": [0.0, 0.0, 0.0, 0.0],
        "plot_path": "plots/hand_ik.png"    // Path to visualization
      },
      "is_valid": true,
      "violations": []
    }
  }
}
```

#### Understanding Joint Angles
- Values are in radians (-π to π)
- Each array represents angles for one finger's joints
- Zero values indicate no rotation
- Example thumb values [-2.98, 0.85] show:
  - Significant knuckle bend (-2.98 radians ≈ -171 degrees)
  - Moderate intermediate joint bend (0.85 radians ≈ 49 degrees)

### 4. Visualization
The system generates a 3D plot (saved as PNG) showing:
- Kinematic chains for each finger (blue lines)
- Target positions (red stars)
- Coordinate axes (X, Y, Z)

## Usage

### 1. Running the Server
```bash
# Basic server
python FlaskBackend/main.py

# With IK processing
python FlaskBackend/main.py --enable-ik

# With IK and plotting
python FlaskBackend/main.py --enable-ik --plot-ik
```

### 2. Sending Requests
```bash
# Test with example data
python FlaskBackend/test_request.py --json_file example.json --enable-ik
```

### 3. Interpreting Results
1. Check `is_valid` for validation status
2. Review `violations` for any validation errors
3. Examine `ik_results` for joint angles
4. View the generated plot at the specified `plot_path`

## Technical Details

### IK Solver
- Uses IKPy library for inverse kinematics calculations
- Employs numerical optimization to find joint angles
- Respects joint constraints (e.g., bend directions)
- Minimizes total joint movement

### Coordinate System
- Origin at hand base
- X: Left/Right
- Y: Forward/Back
- Z: Up/Down
- Units: Meters

### Limitations
1. Assumes fixed base position
2. Simplified finger model (real hands have more complex joints)
3. No collision detection between fingers
4. Joint limits are approximate

## Troubleshooting

### Common Issues
1. Zero angles: May indicate IK solution not found
2. Unexpected positions: Check coordinate system alignment
3. Plot not generated: Ensure write permissions in plots directory 

## Robot Arm Forward Kinematics

### Simplified Robot Configuration
The robot arm is configured with a simplified setup focusing on wrist positioning and pincer control:

1. **End Effector (Pincer)**:
   - Two-finger pincer gripper (actuator 14)
   - Maps to user's thumb and index finger distance
   - Gripper range: 0 (closed) to 1 (fully open)

2. **Wrist Joint**:
   - Maps to user's elbow position
   - Single yaw rotation (actuator 13)
   - Primary joint for position control

3. **Base Reference**:
   - Fixed base position
   - Shoulder joint ignored in first iteration
   - All positions relative to base frame

### Required Parameters
To implement the simplified kinematics:

1. **Physical Measurements**:
   - Wrist to pincer tip length
   - Pincer opening range (min/max distance between fingers)

2. **Joint Properties**:
   - Wrist yaw range (actuator 13)
   - Pincer opening range (actuator 14)

3. **Servo Properties**:
   - Servo position to angle conversion for wrist
   - Servo position to distance conversion for pincer

### Position Mapping Approach

1. **Hand Position Tracking**:
   ```python
   def get_robot_position(self) -> Dict[str, float]:
       # Get wrist position from servo
       wrist_state = self.kos.actuator.get_actuators_state([13])[0]
       pincer_state = self.kos.actuator.get_actuators_state([14])[0]
       
       # Calculate end effector position based on wrist angle
       wrist_angle = wrist_state.position  # in radians
       x = L * cos(wrist_angle)  # L is wrist-to-tip length
       y = L * sin(wrist_angle)
       z = 0  # Simplified 2D movement for first iteration
       
       return {
           'x': x,
           'y': y,
           'z': z,
           'gripper_opening': pincer_state.position
       }
   ```

2. **VR to Robot Mapping**:
   - Track user's thumb and index finger positions
   - Calculate pincer opening from finger distance
   - Map elbow position to wrist rotation
   ```python
   def vr_to_robot_mapping(thumb_pos, index_pos, elbow_pos):
       # Calculate gripper opening from finger distance
       finger_distance = distance(thumb_pos, index_pos)
       gripper_value = scale_to_gripper_range(finger_distance)
       
       # Calculate wrist angle from elbow position
       wrist_angle = calculate_wrist_angle(elbow_pos)
       
       return {
           'wrist_angle': wrist_angle,
           'gripper_value': gripper_value
       }
   ```

### Calibration Process
1. Record key poses:
   - Elbow at center, fingers closed
   - Elbow at extremes, fingers open
   - Multiple points between extremes

2. For each calibration point:
   - Record VR positions (thumb, index, elbow)
   - Record robot positions (wrist angle, pincer opening)
   - Calculate transformation matrix
   - Validate mapping accuracy

3. Save calibration:
   - Wrist angle limits
   - Pincer range mapping
   - Position transformation matrix

### Implementation Requirements
To complete this simplified implementation, please provide:

1. Wrist-to-tip length in meters
2. Pincer opening range (min/max in meters)
3. Wrist servo angle range
4. Pincer servo position to opening distance conversion

This simplified approach focuses on achieving accurate end-effector positioning and gripper control before adding shoulder joint complexity in future iterations. 