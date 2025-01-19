from hand_interface import RoboticHand
import time

def test_individual_fingers():
    """Test moving each finger individually within safe limits."""
    # Note: Replace with your actual serial port
    # Common ports:
    # - Windows: 'COM3' (or similar)
    # - Linux/Mac: '/dev/ttyUSB0' or '/dev/ttyACM0'
    with RoboticHand(port='/dev/ttyUSB0') as hand:
        print("Testing individual finger movements...")
        
        # Test sequence for each finger with safe limits
        fingers = [
            (hand.move_thumb, "Thumb", hand.SERVO_LIMITS['T']),
            (hand.move_index, "Index", hand.SERVO_LIMITS['I']),
            (hand.move_middle, "Middle", hand.SERVO_LIMITS['M']),
            (hand.move_ring, "Ring", hand.SERVO_LIMITS['R']),
            (hand.move_pinky, "Pinky", hand.SERVO_LIMITS['P']),
            (hand.move_wrist, "Wrist", hand.SERVO_LIMITS['W'])
        ]
        
        for move_func, name, (min_angle, max_angle) in fingers:
            print(f"\nTesting {name}...")
            print(f"Safe range: {min_angle}° to {max_angle}°")
            
            # Move to middle position first
            mid_angle = (min_angle + max_angle) // 2
            print(f"Moving {name} to middle position ({mid_angle}°)")
            move_func(mid_angle)
            time.sleep(1)
            
            # Close finger to max safe angle
            print(f"Moving {name} to maximum safe position ({max_angle}°)")
            move_func(max_angle)
            time.sleep(1)
            
            # Open finger to min safe angle
            print(f"Moving {name} to minimum safe position ({min_angle}°)")
            move_func(min_angle)
            time.sleep(1)
            
            # Return to neutral middle
            print(f"Returning {name} to neutral")
            move_func(mid_angle)
            time.sleep(1)

def test_wave():
    """Test a smooth waving motion with all fingers."""
    with RoboticHand(port='/dev/ttyUSB0') as hand:
        print("\nPerforming gentle wave motion...")
        
        # Get the most restrictive angle limits across all fingers
        min_angle = max(limit[0] for limit in hand.SERVO_LIMITS.values())
        max_angle = min(limit[1] for limit in hand.SERVO_LIMITS.values())
        
        # Calculate safe wave range
        wave_min = min_angle + 10
        wave_max = max_angle - 10
        
        for _ in range(2):  # Wave 2 times
            # Wave sequence with smaller increments for smoother motion
            for angle in range(wave_min, wave_max, 15):  # Smaller steps
                hand.move_thumb(angle)
                time.sleep(0.05)  # Small delay between fingers
                hand.move_index(angle)
                time.sleep(0.05)
                hand.move_middle(angle)
                time.sleep(0.05)
                hand.move_ring(angle)
                time.sleep(0.05)
                hand.move_pinky(angle)
                time.sleep(0.05)
            
            for angle in range(wave_max, wave_min, -15):
                hand.move_thumb(angle)
                time.sleep(0.05)
                hand.move_index(angle)
                time.sleep(0.05)
                hand.move_middle(angle)
                time.sleep(0.05)
                hand.move_ring(angle)
                time.sleep(0.05)
                hand.move_pinky(angle)
                time.sleep(0.05)

def main():
    print("Starting hand movement tests (with safety limits)...")
    
    try:
        test_individual_fingers()
        time.sleep(1)
        test_wave()
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except ValueError as e:
        print(f"\nSafety limit exceeded: {str(e)}")
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
    
    print("\nTests completed!")

if __name__ == "__main__":
    main() 