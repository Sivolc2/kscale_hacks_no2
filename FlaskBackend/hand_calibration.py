import numpy as np
from scipy.spatial.transform import Rotation
from typing import Dict, List, Tuple, Optional
import json
import os

class HandCalibration:
    def __init__(self, calibration_file: str = 'calibration.json'):
        """Initialize calibration system
        
        Args:
            calibration_file: Path to calibration data file
        """
        self.calibration_file = calibration_file
        self.transform_matrix = None
        self.scale_factors = None
        self.offset = None
        self.load_calibration()
        
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
    
    def calibrate(self, vr_points: List[Dict[str, float]], 
                 robot_points: List[Dict[str, float]]) -> None:
        """Perform calibration using corresponding points
        
        Args:
            vr_points: List of points from VR space
            robot_points: List of corresponding points in robot space
        """
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