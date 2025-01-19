import numpy as np
from scipy.spatial.transform import Rotation
from typing import Dict, List, Tuple, Optional
import json
import os
import pykos

# Mapping of joint names to IDs (copied from test_movement.py)
ACTUATOR_NAME_TO_ID = {
    "left_shoulder_yaw": 11,
    "left_shoulder_pitch": 12,
    "left_elbow_yaw": 13,
    "left_gripper": 14,
    "right_shoulder_yaw": 21,
    "right_shoulder_pitch": 22,
    "right_elbow_yaw": 23,
    "right_gripper": 24,
}

class HandCalibration:
    def __init__(self, calibration_file: str = 'calibration.json', robot_ip: str = '192.168.42.1', connect_robot: bool = False):
        """Initialize calibration system
        
        Args:
            calibration_file: Path to calibration data file
            robot_ip: IP address of the KOS robot
            connect_robot: Whether to connect to the robot immediately
        """
        self.calibration_file = calibration_file
        self.transform_matrix = None
        self.scale_factors = None
        self.offset = None
        self.robot_ip = robot_ip
        self.kos = None
        
        if connect_robot:
            self.connect_robot()
            
        self.load_calibration()
    
    def connect_robot(self) -> bool:
        """Connect to the robot if not already connected
        
        Returns:
            bool: True if connection successful or already connected
        """
        if self.kos is not None:
            return True
            
        try:
            self.kos = pykos.KOS(ip=self.robot_ip)
            self.setup_robot()
            return True
        except Exception as e:
            print(f"Warning: Could not connect to robot: {e}")
            return False
    
    def setup_robot(self):
        """Configure robot actuators for calibration"""
        if self.kos is None:
            raise RuntimeError("Robot not connected. Call connect_robot() first.")
            
        # Configure left arm actuators
        for actuator_id in [11, 12, 13]:  # left arm actuators
            self.kos.actuator.configure_actuator(
                actuator_id=actuator_id,
                torque_enabled=True,
                kp=120,
                kd=10
            )
    
    def get_robot_position(self) -> Dict[str, float]:
        """Get current robot arm position from servo feedback
        
        Returns:
            Dictionary with x,y,z coordinates calculated from joint positions
        """
        if self.kos is None:
            raise RuntimeError("Robot not connected. Call connect_robot() first.")
            
        # Get current joint positions
        actuator_ids = [11, 12, 13]  # left arm actuators
        states = self.kos.actuator.get_actuators_state(actuator_ids)
        
        # TODO: Implement forward kinematics to convert joint angles to x,y,z position
        # This is a simplified placeholder - you'll need to implement proper forward kinematics
        positions = {state.actuator_id: state.position for state in states.states}
        
        # Simplified conversion - replace with actual forward kinematics
        x = positions[11] * 0.3  # shoulder yaw contribution
        y = positions[12] * 0.3  # shoulder pitch contribution
        z = positions[13] * 0.3  # elbow contribution
        
        return {'x': x, 'y': y, 'z': z}
    
    def load_calibration(self) -> None:
        """Load calibration data from file if it exists"""
        if os.path.exists(self.calibration_file):
            with open(self.calibration_file, 'r') as f:
                data = json.load(f)
                self.transform_matrix = np.array(data['transform_matrix'])
                self.scale_factors = np.array(data['scale_factors'])
                self.offset = np.array(data['offset'])
    
    def save_calibration(self) -> None:
        """Save calibration data to file"""
        data = {
            'transform_matrix': self.transform_matrix.tolist(),
            'scale_factors': self.scale_factors.tolist(),
            'offset': self.offset.tolist()
        }
        with open(self.calibration_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def calibrate(self, vr_points: List[Dict[str, float]]) -> None:
        """Perform calibration using VR points and current robot positions
        
        Args:
            vr_points: List of points from VR space
        """
        # Get corresponding robot points from servo feedback
        robot_points = []
        for _ in vr_points:
            # Prompt user to move robot to corresponding position
            input("Move robot to corresponding position and press Enter...")
            robot_points.append(self.get_robot_position())
        
        # Convert points to numpy arrays
        vr_array = np.array([[p['x'], p['y'], p['z']] for p in vr_points])
        robot_array = np.array([[p['x'], p['y'], p['z']] for p in robot_points])
        
        # Calculate centroid and centered coordinates
        vr_centroid = np.mean(vr_array, axis=0)
        robot_centroid = np.mean(robot_array, axis=0)
        
        vr_centered = vr_array - vr_centroid
        robot_centered = robot_array - robot_centroid
        
        # Calculate scale factors
        vr_scale = np.std(vr_centered, axis=0)
        robot_scale = np.std(robot_centered, axis=0)
        self.scale_factors = robot_scale / vr_scale
        
        # Scale VR points
        vr_scaled = vr_centered * self.scale_factors
        
        # Calculate rotation matrix using SVD
        H = vr_scaled.T @ robot_centered
        U, _, Vt = np.linalg.svd(H)
        R = Vt.T @ U.T
        
        # Ensure right-handed coordinate system
        if np.linalg.det(R) < 0:
            Vt[-1, :] *= -1
            R = Vt.T @ U.T
        
        self.transform_matrix = R
        self.offset = robot_centroid - (R @ (vr_centroid * self.scale_factors))
        
        # Save calibration data
        self.save_calibration()
    
    def transform_point(self, point: Dict[str, float]) -> Dict[str, float]:
        """Transform a point from VR space to robot space
        
        Args:
            point: Point in VR space with x,y,z coordinates
            
        Returns:
            Transformed point in robot space
        """
        if self.transform_matrix is None:
            raise ValueError("Calibration not performed yet")
        
        # Convert to numpy array and apply transformation
        p = np.array([point['x'], point['y'], point['z']])
        p_scaled = p * self.scale_factors
        p_transformed = self.transform_matrix @ p_scaled + self.offset
        
        return {
            'x': float(p_transformed[0]),
            'y': float(p_transformed[1]),
            'z': float(p_transformed[2])
        }
    
    def transform_hand_data(self, hand_data: Dict) -> Dict:
        """Transform all points in hand data from VR space to robot space
        
        Args:
            hand_data: Hand data dictionary with points
            
        Returns:
            Transformed hand data
        """
        transformed_data = hand_data.copy()
        
        # Transform each point in the hand data
        for point in transformed_data['points']:
            transformed_point = self.transform_point(point)
            point.update(transformed_point)
        
        return transformed_data
    
    def get_calibration_poses(self) -> List[Dict[str, float]]:
        """Get list of recommended calibration poses
        
        Returns:
            List of poses for calibration
        """
        # Define key poses for calibration
        return [
            {'name': 'Center', 'description': 'Hand at rest position'},
            {'name': 'Forward Max', 'description': 'Hand fully extended forward'},
            {'name': 'Up Max', 'description': 'Hand raised to maximum height'},
            {'name': 'Side Max', 'description': 'Hand extended to maximum side reach'},
            {'name': 'Down Max', 'description': 'Hand at lowest position'},
        ]
    
    def check_calibration_quality(self, 
                                vr_points: List[Dict[str, float]], 
                                robot_points: List[Dict[str, float]]) -> Dict[str, float]:
        """Check the quality of calibration
        
        Args:
            vr_points: Original VR points
            robot_points: Corresponding robot points
            
        Returns:
            Dictionary with error metrics
        """
        if self.transform_matrix is None:
            raise ValueError("Calibration not performed yet")
        
        errors = []
        for vr_p, robot_p in zip(vr_points, robot_points):
            transformed_p = self.transform_point(vr_p)
            error = np.sqrt(sum((transformed_p[k] - robot_p[k])**2 
                              for k in ['x', 'y', 'z']))
            errors.append(error)
        
        return {
            'mean_error': float(np.mean(errors)),
            'max_error': float(np.max(errors)),
            'std_error': float(np.std(errors))
        } 