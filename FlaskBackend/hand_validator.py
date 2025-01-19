import pandas as pd
from typing import Dict, List, Tuple, Any

class HandValidator:
    def __init__(self, rules_file: str):
        """Initialize the validator with rules from a CSV file.
        
        Args:
            rules_file (str): Path to the CSV file containing validation rules
        """
        self.rules = pd.read_csv(rules_file)
        # Convert rules to a dictionary for faster lookup
        self.rules_dict = self.rules.set_index('point_name').to_dict('index')
    
    def validate_point(self, point: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a single point against the rules.
        
        Args:
            point (dict): Point data containing name and coordinates
            
        Returns:
            tuple: (is_valid, list of violations)
        """
        violations = []
        point_name = point['name']
        
        # Skip validation if point is not in rules
        if point_name not in self.rules_dict:
            return True, []
            
        rules = self.rules_dict[point_name]
        
        # Check X coordinate
        if point['x'] < rules['min_x'] or point['x'] > rules['max_x']:
            violations.append(f"{point_name} x-coordinate {point['x']} is outside range [{rules['min_x']}, {rules['max_x']}]")
            
        # Check Y coordinate
        if point['y'] < rules['min_y'] or point['y'] > rules['max_y']:
            violations.append(f"{point_name} y-coordinate {point['y']} is outside range [{rules['min_y']}, {rules['max_y']}]")
            
        # Check Z coordinate
        if point['z'] < rules['min_z'] or point['z'] > rules['max_z']:
            violations.append(f"{point_name} z-coordinate {point['z']} is outside range [{rules['min_z']}, {rules['max_z']}]")
            
        return len(violations) == 0, violations
    
    def validate_hand(self, hand_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate all points in a hand against the rules.
        
        Args:
            hand_data (dict): Hand data containing points
            
        Returns:
            tuple: (is_valid, list of violations)
        """
        all_violations = []
        
        for point in hand_data['points']:
            is_valid, violations = self.validate_point(point)
            all_violations.extend(violations)
            
        return len(all_violations) == 0, all_violations 