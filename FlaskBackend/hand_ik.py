from ikpy.chain import Chain
from ikpy.link import OriginLink, URDFLink
import numpy as np
import matplotlib
# Use Agg backend (non-GUI)
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from typing import Dict, List, Any
import os

class HandIK:
    def __init__(self):
        """Initialize the IK chains for fingers"""
        self.fingers = {
            'thumb': self._create_thumb_chain(),
            'index': self._create_finger_chain('index'),
            'middle': self._create_finger_chain('middle'),
            'ring': self._create_finger_chain('ring'),
            'little': self._create_finger_chain('little')
        }
        
        # Create plots directory if it doesn't exist
        os.makedirs('plots', exist_ok=True)
        
    def _create_thumb_chain(self) -> Chain:
        """Create IK chain for thumb with 4 joints"""
        return Chain(name='thumb', links=[
            OriginLink(),
            URDFLink(
                name="thumb_knuckle",
                origin_translation=[0, 0, 0],
                origin_orientation=[0, 0, 0],
                rotation=[1, 1, 1]  # Allow rotation in all axes
            ),
            URDFLink(
                name="thumb_intermediate",
                origin_translation=[0, 0, 0.02],  # 2cm length
                origin_orientation=[0, 0, 0],
                rotation=[0, 1, 0]  # Bend only
            ),
            URDFLink(
                name="thumb_tip",
                origin_translation=[0, 0, 0.02],
                origin_orientation=[0, 0, 0],
                rotation=[0, 1, 0]
            )
        ])
    
    def _create_finger_chain(self, name: str) -> Chain:
        """Create IK chain for a finger with 3 joints"""
        return Chain(name=name, links=[
            OriginLink(),
            URDFLink(
                name=f"{name}_knuckle",
                origin_translation=[0, 0, 0],
                origin_orientation=[0, 0, 0],
                rotation=[1, 1, 0]  # Allow flexion and abduction
            ),
            URDFLink(
                name=f"{name}_intermediate",
                origin_translation=[0, 0, 0.03],  # 3cm length
                origin_orientation=[0, 0, 0],
                rotation=[0, 1, 0]  # Bend only
            ),
            URDFLink(
                name=f"{name}_tip",
                origin_translation=[0, 0, 0.02],
                origin_orientation=[0, 0, 0],
                rotation=[0, 1, 0]
            )
        ])
    
    def process_hand(self, hand_data: Dict[str, Any], plot: bool = False) -> Dict[str, Any]:
        """Process hand data and optionally plot it
        
        Args:
            hand_data: Dictionary containing hand points
            plot: Whether to save plot to file
            
        Returns:
            Dictionary with IK solutions for each finger and plot file path if plotting enabled
        """
        # Extract points by finger
        points_by_finger = self._organize_points_by_finger(hand_data['points'])
        
        # Process each finger
        results = {}
        fig = None
        ax = None
        plot_path = None
        
        if plot:
            fig = plt.figure(figsize=(10, 10))
            ax = fig.add_subplot(111, projection='3d')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
        
        for finger_name, chain in self.fingers.items():
            if finger_name in points_by_finger:
                points = points_by_finger[finger_name]
                # Get tip position
                target = [points[-1]['x'], points[-1]['y'], points[-1]['z']]
                
                # Compute IK
                ik_solution = chain.inverse_kinematics(target)
                results[finger_name] = ik_solution.tolist()
                
                if plot and ax:
                    # Plot the chain
                    chain.plot(ik_solution, ax, show=False)
                    # Plot the target point
                    ax.scatter([target[0]], [target[1]], [target[2]], c='red', marker='*')
        
        if plot:
            plt.title('Hand IK Visualization')
            # Save plot to file
            plot_path = os.path.join('plots', 'hand_ik.png')
            plt.savefig(plot_path)
            plt.close()
            results['plot_path'] = plot_path
        
        return results
    
    def _organize_points_by_finger(self, points: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Organize points by finger name"""
        fingers = {
            'thumb': [],
            'index': [],
            'middle': [],
            'ring': [],
            'little': []
        }
        
        for point in points:
            name = point['name'].lower()
            if 'thumb' in name:
                fingers['thumb'].append(point)
            elif 'index' in name:
                fingers['index'].append(point)
            elif 'middle' in name:
                fingers['middle'].append(point)
            elif 'ring' in name:
                fingers['ring'].append(point)
            elif 'little' in name:
                fingers['little'].append(point)
                
        return fingers 