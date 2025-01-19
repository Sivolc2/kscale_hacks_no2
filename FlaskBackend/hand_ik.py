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
from datetime import datetime
from hand_calibration import HandCalibration

class HandIK:
    def __init__(self, calibration_file: str = 'calibration.json'):
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
        
        # Initialize calibration
        self.calibration = HandCalibration(calibration_file)
        
    def calibrate(self, vr_points: List[Dict[str, float]], 
                 robot_points: List[Dict[str, float]]) -> Dict[str, float]:
        """Perform calibration with the given points
        
        Args:
            vr_points: List of points from VR space
            robot_points: List of corresponding points in robot space
            
        Returns:
            Calibration quality metrics
        """
        self.calibration.calibrate(vr_points, robot_points)
        return self.calibration.check_calibration_quality(vr_points, robot_points)

    def get_calibration_poses(self) -> List[Dict[str, float]]:
        """Get recommended calibration poses"""
        return self.calibration.get_calibration_poses()

    def _plot_finger_chain(self, chain: Chain, ik_solution: np.ndarray, ax: Axes3D, color: str = 'blue'):
        """Plot only the finger segments without the extended lines
        
        Args:
            chain: IKPy chain object
            ik_solution: Joint angles
            ax: Matplotlib 3D axis
            color: Color for the finger segments
        """
        # Get transformation matrices for each joint
        transforms = chain.forward_kinematics(ik_solution, full_kinematics=True)
        
        # Extract joint positions
        positions = []
        for transform in transforms:
            # Get the translation part of the transformation matrix
            pos = transform[:3, 3]
            positions.append(pos)
        
        # Convert to numpy array for easier manipulation
        positions = np.array(positions)
        
        # Plot segments between joints
        for i in range(len(positions) - 1):
            ax.plot([positions[i][0], positions[i+1][0]],
                   [positions[i][1], positions[i+1][1]],
                   [positions[i][2], positions[i+1][2]],
                   color=color, linewidth=2)
            
            # Plot joint as a small sphere
            ax.scatter(positions[i][0], positions[i][1], positions[i][2],
                      color=color, s=50)
        
        # Plot last joint
        ax.scatter(positions[-1][0], positions[-1][1], positions[-1][2],
                  color=color, s=50)
        
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

    def _get_plot_limits(self, points_by_finger: Dict[str, List[Dict[str, Any]]]) -> tuple:
        """Calculate appropriate axis limits based on hand points
        
        Args:
            points_by_finger: Dictionary of points organized by finger
            
        Returns:
            tuple: (min_x, max_x, min_y, max_y, min_z, max_z)
        """
        all_points = []
        for finger_points in points_by_finger.values():
            all_points.extend(finger_points)
        
        if not all_points:
            return (-0.1, 0.1, -0.1, 0.1, -0.1, 0.1)
        
        # Get min and max for each coordinate
        x_coords = [p['x'] for p in all_points]
        y_coords = [p['y'] for p in all_points]
        z_coords = [p['z'] for p in all_points]
        
        # Calculate ranges
        x_range = max(x_coords) - min(x_coords)
        y_range = max(y_coords) - min(y_coords)
        z_range = max(z_coords) - min(z_coords)
        
        # Add padding (20% of the range)
        padding = 0.2
        x_pad = x_range * padding
        y_pad = y_range * padding
        z_pad = z_range * padding
        
        return (
            min(x_coords) - x_pad, max(x_coords) + x_pad,
            min(y_coords) - y_pad, max(y_coords) + y_pad,
            min(z_coords) - z_pad, max(z_coords) + z_pad
        )
    
    def process_hand(self, hand_data: Dict[str, Any], plot: bool = False, 
                    hand_id: str = None, source_file: str = None, 
                    apply_calibration: bool = True) -> Dict[str, Any]:
        """Process hand data and optionally plot it
        
        Args:
            hand_data: Dictionary containing hand points
            plot: Whether to save plot to file
            hand_id: Identifier for the hand (left/right)
            source_file: Name of the source JSON file
            apply_calibration: Whether to apply calibration transform
            
        Returns:
            Dictionary with IK solutions for each finger and plot file path if plotting enabled
        """
        # Apply calibration if requested
        if apply_calibration:
            try:
                hand_data = self.calibration.transform_hand_data(hand_data)
            except ValueError as e:
                print(f"Warning: Calibration not applied - {str(e)}")
        
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
            
            # Set axis limits based on hand points
            x_min, x_max, y_min, y_max, z_min, z_max = self._get_plot_limits(points_by_finger)
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_zlim(z_min, z_max)
            
            # Make the plot aspect ratio equal
            max_range = max(x_max - x_min, y_max - y_min, z_max - z_min)
            mid_x = (x_max + x_min) * 0.5
            mid_y = (y_max + y_min) * 0.5
            mid_z = (z_max + z_min) * 0.5
            ax.set_xlim(mid_x - max_range * 0.5, mid_x + max_range * 0.5)
            ax.set_ylim(mid_y - max_range * 0.5, mid_y + max_range * 0.5)
            ax.set_zlim(mid_z - max_range * 0.5, mid_z + max_range * 0.5)
            
            # Set a good viewing angle
            ax.view_init(elev=30, azim=45)
        
        # Define colors for each finger
        finger_colors = {
            'thumb': '#1f77b4',    # blue
            'index': '#ff7f0e',    # orange
            'middle': '#2ca02c',   # green
            'ring': '#d62728',     # red
            'little': '#9467bd'    # purple
        }
        
        for finger_name, chain in self.fingers.items():
            if finger_name in points_by_finger:
                points = points_by_finger[finger_name]
                # Sort points by their order in the finger
                points.sort(key=lambda x: x['id'])
                
                # Get all joint positions
                joint_positions = [(p['x'], p['y'], p['z']) for p in points]
                
                # Get tip position for IK
                target = [points[-1]['x'], points[-1]['y'], points[-1]['z']]
                
                # Compute IK
                ik_solution = chain.inverse_kinematics(target)
                results[finger_name] = ik_solution.tolist()
                
                if plot and ax:
                    # Plot actual joint positions and segments
                    for i in range(len(joint_positions) - 1):
                        p1 = joint_positions[i]
                        p2 = joint_positions[i + 1]
                        # Plot segment
                        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]],
                               color=finger_colors[finger_name], linewidth=2, linestyle='-')
                        # Plot joint
                        ax.scatter(p1[0], p1[1], p1[2], 
                                 color=finger_colors[finger_name], s=50)
                    
                    # Plot last joint
                    ax.scatter(joint_positions[-1][0], joint_positions[-1][1], joint_positions[-1][2],
                             color=finger_colors[finger_name], s=50)
                    
                    # Plot IK chain for comparison
                    self._plot_finger_chain(chain, ik_solution, ax, color=finger_colors[finger_name])
                    
                    # Plot target point
                    ax.scatter([target[0]], [target[1]], [target[2]], 
                             c='red', marker='*', s=100)
                    
                    # Add text label for the finger
                    ax.text(target[0], target[1], target[2], 
                           f' {finger_name}', fontsize=8)
        
        if plot:
            # Generate plot filename using source file name and hand ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(os.path.basename(source_file))[0] if source_file else "hand"
            hand_suffix = f"_{hand_id}" if hand_id else ""
            plot_filename = f"{base_name}{hand_suffix}_{timestamp}.png"
            
            plt.title(f'Hand IK Visualization - {base_name}{hand_suffix}')
            # Save plot to file with higher DPI for better quality
            plot_path = os.path.join('plots', plot_filename)
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
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