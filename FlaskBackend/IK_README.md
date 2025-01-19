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

### Required Robot Parameters
To implement accurate forward kinematics for the robot arm, we need:

1. **Link Lengths**:
   - Shoulder to elbow length (l1)
   - Elbow to wrist/end-effector length (l2)

2. **Joint Configuration**:
   - Shoulder yaw axis orientation (typically Z-axis rotation)
   - Shoulder pitch axis orientation (typically Y-axis rotation)
   - Elbow yaw axis orientation (typically Z-axis rotation)

3. **Joint Limits**:
   - Min/max angles for each joint
   - Shoulder yaw range (actuator 11)
   - Shoulder pitch range (actuator 12)
   - Elbow yaw range (actuator 13)

4. **Zero Position Reference**:
   - Default arm configuration when all joints are at 0
   - Reference frame orientation

### Forward Kinematics Approach
We will use the Denavit-Hartenberg (DH) parameters approach:

1. **Coordinate Frames**:
   ```
   Base (0) -> Shoulder Yaw (1) -> Shoulder Pitch (2) -> Elbow Yaw (3) -> End Effector (4)
   ```

2. **Transformation Matrices**:
   - Each joint contributes a rotation and translation
   - For shoulder yaw (θ1):
     ```
     R1 = Rz(θ1)  # Rotation around Z axis
     ```
   - For shoulder pitch (θ2):
     ```
     R2 = Ry(θ2)  # Rotation around Y axis
     T2 = [l1, 0, 0]  # Translation along X
     ```
   - For elbow yaw (θ3):
     ```
     R3 = Rz(θ3)  # Rotation around Z axis
     T3 = [l2, 0, 0]  # Translation along X
     ```

3. **Final Position Calculation**:
   ```python
   def forward_kinematics(theta1, theta2, theta3):
       # Combine transformations
       T_total = T0_1(theta1) @ T1_2(theta2) @ T2_3(theta3)
       # Extract end effector position
       position = T_total[0:3, 3]
       return position
   ```

### Implementation Requirements
To complete the forward kinematics implementation, please provide:

1. Link lengths (l1, l2) in meters
2. Joint angle ranges for each actuator
3. Zero position configuration
4. Confirmation of the axis orientations described above

The current placeholder in `get_robot_position()` uses a simplified linear scaling:
```python
x = positions[11] * 0.3  # shoulder yaw
y = positions[12] * 0.3  # shoulder pitch
z = positions[13] * 0.3  # elbow yaw
```

This will be replaced with proper forward kinematics once the above parameters are confirmed.

### Calibration Process
1. Record VR points in various poses
2. Move robot arm to matching positions
3. Read joint angles from servos
4. Calculate end-effector position using forward kinematics
5. Use these positions for the calibration transform

This approach will provide more accurate position mapping between VR and robot space compared to the current linear approximation. 