from collections import deque
from datetime import datetime

class SimProcessor:
    def __init__(self):
        """Initialize the simulation processor."""
        self.current_position = {
            "rightArm": {"x": 0, "y": 0, "z": 30},
            "leftArm": {"x": 0, "y": 0, "z": 30}
        }
        
        # Request cache using deque for efficient fixed-size queue
        self.request_cache = deque(maxlen=10)
        
        # Mapping of hand points to robot controls
        self.hand_mapping = {
            # Key hand points that control robot movement
            "wrist": "arm_base_position",  # Changed from handWrist to match actual data
            "indexFingerTip": "arm_direction",  # Changed from handIndexFingerTip
            "thumbTip": "arm_rotation"  # Changed from handThumbTip
        }
        
        # Scaling factors for converting hand coordinates to robot coordinates
        self.scaling = {
            "position": {
                "x": 100.0,  # Increased for wider movement
                "y": 75.0,   # Adjusted for height range
                "z": 100.0   # Increased for depth range
            },
            "rotation": 180.0  # Scale rotations to degrees
        }
        
        # Coordinate system adjustments
        self.offset = {
            "x": 0.0,      # No x offset needed
            "y": -1.0,     # Center the y-coordinate (typical range 0.8-1.3)
            "z": 0.3       # Shift z to positive range (-0.3-0.0 -> 0-0.3)
        }

    def _cache_request(self, request_data, processed_result):
        """Cache a request and its processed result.
        
        Args:
            request_data (dict): The original request data
            processed_result (dict): The processed result
        """
        cache_entry = {
            "timestamp": datetime.now().isoformat(),
            "request": request_data,
            "result": processed_result
        }
        self.request_cache.append(cache_entry)

    def get_cached_requests(self):
        """Get the cached requests.
        
        Returns:
            list: List of cached requests, most recent first
        """
        return list(self.request_cache)

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
            if "wrist" in points:
                wrist = points["wrist"]
                # Apply coordinate transformation and scaling
                processed_data["pose"][arm_key] = {
                    "x": self._clamp((wrist["x"] + self.offset["x"]) * self.scaling["position"]["x"], -50, 50),
                    "y": self._clamp((wrist["y"] + self.offset["y"]) * self.scaling["position"]["y"], -50, 50),
                    "z": self._clamp((wrist["z"] + self.offset["z"]) * self.scaling["position"]["z"], 0, 60)
                }
                
                # Calculate additional transformations based on finger positions
                if "indexFingerTip" in points and "thumbTip" in points:
                    index_tip = points["indexFingerTip"]
                    thumb_tip = points["thumbTip"]
                    
                    # Calculate relative positions for finer control
                    dx = (index_tip["x"] - wrist["x"]) * self.scaling["position"]["x"] * 0.5
                    dy = (index_tip["y"] - wrist["y"]) * self.scaling["position"]["y"] * 0.5
                    dz = (index_tip["z"] - wrist["z"]) * self.scaling["position"]["z"] * 0.5
                    
                    # Apply the fine adjustments to the arm position
                    processed_data["pose"][arm_key]["x"] = self._clamp(processed_data["pose"][arm_key]["x"] + dx, -50, 50)
                    processed_data["pose"][arm_key]["y"] = self._clamp(processed_data["pose"][arm_key]["y"] + dy, -50, 50)
                    processed_data["pose"][arm_key]["z"] = self._clamp(processed_data["pose"][arm_key]["z"] + dz, 0, 60)
            
            # Update current position
            self.current_position[arm_key] = processed_data["pose"][arm_key]
        
        # Add debug information
        processed_data["debug"] = {
            "original_data": headset_data,
            "mapping_used": self.hand_mapping,
            "scaling_factors": self.scaling,
            "offsets": self.offset,
            "processed_points": {
                "left": list(points.keys()) if "left_hand" in headset_data.get("hands", {}) else [],
                "right": list(points.keys()) if "right_hand" in headset_data.get("hands", {}) else []
            }
        }
        
        # Cache the request and result
        self._cache_request(headset_data, processed_data)
        
        return processed_data

    def _clamp(self, value, min_val, max_val):
        """Clamp a value between min and max values."""
        return max(min(value, max_val), min_val)

    def get_current_position(self):
        """Get the current position of the simulated robot."""
        return {"pose": self.current_position.copy()} 
