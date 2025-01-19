import unittest
from hand_ik import HandIK
import numpy as np

class TestHandIK(unittest.TestCase):
    def setUp(self):
        self.ik_processor = HandIK()
        
    def test_process_hand(self):
        # Test hand data with realistic finger positions
        test_hand = {
            "points": [
                # Thumb points
                {"name": "handThumbKnuckle", "x": 0.15, "y": 0.25, "z": 0.35},
                {"name": "handThumbIntermediateBase", "x": 0.2, "y": 0.3, "z": 0.4},
                {"name": "handThumbTip", "x": 0.3, "y": 0.4, "z": 0.5},
                
                # Index finger points
                {"name": "handIndexFingerKnuckle", "x": 0.4, "y": 0.5, "z": 0.6},
                {"name": "handIndexFingerIntermediateBase", "x": 0.45, "y": 0.55, "z": 0.65},
                {"name": "handIndexFingerTip", "x": 0.55, "y": 0.65, "z": 0.75},
                
                # Middle finger points
                {"name": "handMiddleFingerKnuckle", "x": 0.65, "y": 0.75, "z": 0.85},
                {"name": "handMiddleFingerIntermediateBase", "x": 0.7, "y": 0.8, "z": 0.9},
                {"name": "handMiddleFingerTip", "x": 0.8, "y": 0.9, "z": 1.0}
            ]
        }
        
        # Process without plotting
        results = self.ik_processor.process_hand(test_hand, plot=False)
        
        # Check that we got results for each finger in the test data
        self.assertIn('thumb', results)
        self.assertIn('index', results)
        self.assertIn('middle', results)
        
        # Check that each result is a list of joint angles
        for finger_name, angles in results.items():
            self.assertIsInstance(angles, list)
            # Each finger should have angles for each joint
            self.assertGreater(len(angles), 0)
            
            # Check that angles are within reasonable ranges (-pi to pi)
            for angle in angles:
                self.assertGreaterEqual(angle, -np.pi)
                self.assertLessEqual(angle, np.pi)
    
    def test_organize_points(self):
        test_points = [
            {"name": "handThumbTip", "x": 0, "y": 0, "z": 0},
            {"name": "handIndexFingerTip", "x": 0, "y": 0, "z": 0},
            {"name": "handMiddleFingerTip", "x": 0, "y": 0, "z": 0},
            {"name": "handRingFingerTip", "x": 0, "y": 0, "z": 0},
            {"name": "handLittleFingerTip", "x": 0, "y": 0, "z": 0}
        ]
        
        organized = self.ik_processor._organize_points_by_finger(test_points)
        
        # Check that all fingers are present
        self.assertEqual(len(organized), 5)
        self.assertIn('thumb', organized)
        self.assertIn('index', organized)
        self.assertIn('middle', organized)
        self.assertIn('ring', organized)
        self.assertIn('little', organized)
        
        # Check that points were correctly categorized
        self.assertEqual(len(organized['thumb']), 1)
        self.assertEqual(len(organized['index']), 1)
        self.assertEqual(len(organized['middle']), 1)
        self.assertEqual(len(organized['ring']), 1)
        self.assertEqual(len(organized['little']), 1)

if __name__ == '__main__':
    unittest.main() 