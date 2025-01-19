import unittest
from hand_validator import HandValidator
import json

class TestHandValidator(unittest.TestCase):
    def setUp(self):
        self.validator = HandValidator('validation.csv')
        
    def test_valid_hand(self):
        # Valid hand data where all points are within range
        valid_hand = {
            "points": [
                {"name": "handWrist", "x": 0.1, "y": 0.2, "z": 0.3},
                {"name": "handThumbTip", "x": 0.3, "y": 0.4, "z": 0.5},
                {"name": "handIndexFingerTip", "x": 0.55, "y": 0.65, "z": 0.75},
                {"name": "handMiddleFingerTip", "x": 0.8, "y": 0.9, "z": 1.0},
                {"name": "handRingFingerTip", "x": 1.05, "y": 1.15, "z": 1.25},
                {"name": "handLittleFingerTip", "x": 1.3, "y": 1.4, "z": 1.5}
            ]
        }
        
        is_valid, violations = self.validator.validate_hand(valid_hand)
        self.assertTrue(is_valid)
        self.assertEqual(len(violations), 0)
        print("Valid hand data passed the test.")
        
    def test_invalid_hand(self):
        # Invalid hand data where points are outside the allowed range
        invalid_hand = {
            "points": [
                {"name": "handWrist", "x": 2.5, "y": 2.5, "z": 2.5},  # Outside range
                {"name": "handThumbTip", "x": 0.3, "y": 0.4, "z": 0.5},
                {"name": "handIndexFingerTip", "x": -1.0, "y": 0.65, "z": 0.75},  # Outside range
                {"name": "handMiddleFingerTip", "x": 0.8, "y": 0.9, "z": 1.0},
                {"name": "handRingFingerTip", "x": 1.05, "y": 1.15, "z": 1.25},
                {"name": "handLittleFingerTip", "x": 1.3, "y": 3.0, "z": 1.5}  # Outside range
            ]
        }
        
        is_valid, violations = self.validator.validate_hand(invalid_hand)
        self.assertFalse(is_valid)
        self.assertGreater(len(violations), 0)
        print("Invalid hand data failed the test.")

if __name__ == '__main__':
    unittest.main() 