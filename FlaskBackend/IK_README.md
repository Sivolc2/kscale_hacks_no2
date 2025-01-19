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