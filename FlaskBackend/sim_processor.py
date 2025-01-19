class SimProcessor:
    def __init__(self):
        """Initialize the simulation processor."""
        self.current_position = {
            "rightArm": {"x": 0, "y": 0, "z": 30},
            "leftArm": {"x": 0, "y": 0, "z": 30}
        }
        
        # Mapping of hand points to robot controls
        self.hand_mapping = {
            # Key hand points that control robot movement
            "handWrist": "arm_base_position",
            "handIndexFingerTip": "arm_direction",
            "handThumbTip": "arm_rotation",
            # Add more mappings as needed
        }
        
        # Scaling factors for converting hand coordinates to robot coordinates
        self.scaling = {
            "position": 50.0,  # Scale hand position to robot workspace
            "rotation": 180.0  # Scale rotations to degrees
        }

    def process_movement(self, movement_data):
        """Process incoming movement data and return updated position.
        
        Args:
            movement_data (dict): Input movement data containing target positions
            
        Returns:
            dict: Processed movement data with updated positions
        """
        # For now, just echo back the movement data with some basic validation
        processed_data = {"pose": {}}
        
        # Add debug information
        processed_data["debug"] = {
            "original_data": movement_data,
            "assumptions": {
                "x_y_range": "Clamped between -50 and 50",
                "z_range": "Clamped between 0 and 60",
                "missing_coords": "Defaulting to 0 for x/y, 30 for z"
            }
        }
        
        # Process right arm if present
        if "rightArm" in movement_data:
            processed_data["pose"]["rightArm"] = {
                "x": self._clamp(movement_data["rightArm"].get("x", 0), -50, 50),
                "y": self._clamp(movement_data["rightArm"].get("y", 0), -50, 50),
                "z": self._clamp(movement_data["rightArm"].get("z", 30), 0, 60)
            }
            self.current_position["rightArm"] = processed_data["pose"]["rightArm"]

        # Process left arm if present
        if "leftArm" in movement_data:
            processed_data["pose"]["leftArm"] = {
                "x": self._clamp(movement_data["leftArm"].get("x", 0), -50, 50),
                "y": self._clamp(movement_data["leftArm"].get("y", 0), -50, 50),
                "z": self._clamp(movement_data["leftArm"].get("z", 30), 0, 60)
            }
            self.current_position["leftArm"] = processed_data["pose"]["leftArm"]

        # Add processing results to debug info
        processed_data["debug"]["processed"] = {
            "rightArm": self.current_position["rightArm"] if "rightArm" in movement_data else "not updated",
            "leftArm": self.current_position["leftArm"] if "leftArm" in movement_data else "not updated"
        }

        return processed_data

    def process_headset_data(self, headset_data):
        """Process complex hand tracking data into simplified robot movements.
        
        Args:
            headset_data (dict): Complex hand tracking data with points for both hands
            
        Returns:
            dict: Simplified robot movement data
        """
        processed_data = {"pose": {}}
        
        # Process each hand if present
        for hand_key in ["left_hand", "right_hand"]:
            if hand_key not in headset_data.get("hands", {}):
                continue
                
            hand_data = headset_data["hands"][hand_key]
            arm_key = "leftArm" if hand_key == "left_hand" else "rightArm"
            
            # Create point lookup for easier access
            points = {point["name"]: point for point in hand_data["points"]}
            
            # Calculate arm position from wrist position
            if "handWrist" in points:
                wrist = points["handWrist"]
                processed_data["pose"][arm_key] = {
                    # Scale and transform coordinates
                    # TODO: Add more sophisticated coordinate transformation
                    "x": self._clamp(wrist["x"] * self.scaling["position"], -50, 50),
                    "y": self._clamp(wrist["y"] * self.scaling["position"], -50, 50),
                    "z": self._clamp(wrist["z"] * self.scaling["position"], 0, 60)
                }
                
                # Calculate additional transformations based on finger positions
                if "handIndexFingerTip" in points and "handThumbTip" in points:
                    index_tip = points["handIndexFingerTip"]
                    thumb_tip = points["handThumbTip"]
                    
                    # TODO: Add sophisticated finger position processing
                    # For now, just use relative positions for rotation
                    dx = index_tip["x"] - thumb_tip["x"]
                    dy = index_tip["y"] - thumb_tip["y"]
                    dz = index_tip["z"] - thumb_tip["z"]
                    
                    # Apply transformations to the arm position
                    # This is a placeholder for more complex transformations
                    processed_data["pose"][arm_key]["x"] += self._clamp(dx * 10, -10, 10)
                    processed_data["pose"][arm_key]["y"] += self._clamp(dy * 10, -10, 10)
                    processed_data["pose"][arm_key]["z"] += self._clamp(dz * 10, -10, 10)
            
            # Update current position
            self.current_position[arm_key] = processed_data["pose"][arm_key]
        
        # Add debug information
        processed_data["debug"] = {
            "original_data": headset_data,
            "mapping_used": self.hand_mapping,
            "scaling_factors": self.scaling,
            "processed_points": {
                "left": list(points.keys()) if "left_hand" in headset_data.get("hands", {}) else [],
                "right": list(points.keys()) if "right_hand" in headset_data.get("hands", {}) else []
            }
        }
        
        return processed_data

    def _clamp(self, value, min_val, max_val):
        """Clamp a value between min and max values."""
        return max(min(value, max_val), min_val)

    def get_current_position(self):
        """Get the current position of the simulated robot."""
        return {"pose": self.current_position.copy()} 
