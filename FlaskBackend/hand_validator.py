import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class HandValidator:
    def __init__(self, ruleset_path: str):
        self.rules = pd.read_csv(ruleset_path)
        self.rules.set_index('joint_name', inplace=True)
    
    def calculate_angle(self, p1: Dict, p2: Dict, p3: Dict) -> float:
        """Calculate angle between three points in 3D space"""
        v1 = np.array([p1['x'] - p2['x'], p1['y'] - p2['y'], p1['z'] - p2['z']])
        v2 = np.array([p3['x'] - p2['x'], p3['y'] - p2['y'], p3['z'] - p2['z']])
        
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        return np.degrees(angle)
    
    def validate_hand(self, hand_data: Dict) -> Tuple[bool, List[Dict]]:
        points = {point['name']: point for point in hand_data['points']}
        violations = []
        
        # Define joint chains for angle calculations
        joint_chains = {
            'handThumbKnuckle': ('handWrist', 'handThumbKnuckle', 'handThumbIntermediateBase'),
            'handThumbIntermediateBase': ('handThumbKnuckle', 'handThumbIntermediateBase', 'handThumbIntermediateTip'),
            'handThumbIntermediateTip': ('handThumbIntermediateBase', 'handThumbIntermediateTip', 'handThumbTip'),
            # Add more joint chains for other fingers...
        }
        
        for joint_name, (p1_name, p2_name, p3_name) in joint_chains.items():
            if joint_name in self.rules.index:
                angle = self.calculate_angle(
                    points[p1_name],
                    points[p2_name],
                    points[p3_name]
                )
                
                min_angle = self.rules.loc[joint_name, 'min_angle_degrees']
                max_angle = self.rules.loc[joint_name, 'max_angle_degrees']
                
                if angle < min_angle or angle > max_angle:
                    violations.append({
                        'joint': joint_name,
                        'calculated_angle': angle,
                        'allowed_range': f'{min_angle} to {max_angle}'
                    })
        
        return len(violations) == 0, violations 