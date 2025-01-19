import serial
import time
from typing import Optional, Dict, Tuple

class RoboticHand:
    """Interface for controlling a 6-servo robotic hand via Arduino."""
    
    # Define safe operating ranges for each servo
    SERVO_LIMITS: Dict[str, Tuple[int, int]] = {
        'T': (20, 160),    # Thumb: avoid extreme angles
        'I': (10, 170),    # Index
        'M': (10, 170),    # Middle
        'R': (10, 170),    # Ring
        'P': (10, 170),    # Pinky
        'W': (30, 150),    # Wrist: more restricted to prevent cable strain
    }
    
    def __init__(self, port: str = '/dev/ttyUSB0', baudrate: int = 115200):
        """Initialize the hand interface.
        
        Args:
            port: Serial port where Arduino is connected
            baudrate: Communication speed (should match Arduino sketch)
        """
        self.serial = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset
        
        # Store current positions
        self.current_positions = {
            'T': 90, 'I': 90, 'M': 90, 'R': 90, 'P': 90, 'W': 90
        }
    
    def _is_safe_angle(self, servo: str, angle: int) -> bool:
        """Check if the target angle is within safe limits.
        
        Args:
            servo: Servo identifier
            angle: Target angle
            
        Returns:
            bool: True if angle is safe
        """
        min_angle, max_angle = self.SERVO_LIMITS[servo]
        return min_angle <= angle <= max_angle
    
    def _send_command(self, servo: str, angle: int) -> bool:
        """Send a command to the Arduino and verify response.
        
        Args:
            servo: Single character servo identifier (T,I,M,R,P,W)
            angle: Desired angle between 0 and 180
            
        Returns:
            bool: True if command was successful
        """
        if not (0 <= angle <= 180):
            raise ValueError("Angle must be between 0 and 180")
            
        command = f"{servo},{angle}\n"
        self.serial.write(command.encode())
        response = self.serial.readline().decode().strip()
        return response == "OK"
    
    def move_thumb(self, angle: int) -> bool:
        """Move thumb servo to specified angle."""
        if not self._is_safe_angle('T', angle):
            raise ValueError(f"Angle {angle} is outside safe range {self.SERVO_LIMITS['T']}")
        success = self._send_command('T', angle)
        if success:
            self.current_positions['T'] = angle
        return success
        
    def move_index(self, angle: int) -> bool:
        """Move index finger servo to specified angle."""
        if not self._is_safe_angle('I', angle):
            raise ValueError(f"Angle {angle} is outside safe range {self.SERVO_LIMITS['I']}")
        success = self._send_command('I', angle)
        if success:
            self.current_positions['I'] = angle
        return success
        
    def move_middle(self, angle: int) -> bool:
        """Move middle finger servo to specified angle."""
        if not self._is_safe_angle('M', angle):
            raise ValueError(f"Angle {angle} is outside safe range {self.SERVO_LIMITS['M']}")
        success = self._send_command('M', angle)
        if success:
            self.current_positions['M'] = angle
        return success
        
    def move_ring(self, angle: int) -> bool:
        """Move ring finger servo to specified angle."""
        if not self._is_safe_angle('R', angle):
            raise ValueError(f"Angle {angle} is outside safe range {self.SERVO_LIMITS['R']}")
        success = self._send_command('R', angle)
        if success:
            self.current_positions['R'] = angle
        return success
        
    def move_pinky(self, angle: int) -> bool:
        """Move pinky servo to specified angle."""
        if not self._is_safe_angle('P', angle):
            raise ValueError(f"Angle {angle} is outside safe range {self.SERVO_LIMITS['P']}")
        success = self._send_command('P', angle)
        if success:
            self.current_positions['P'] = angle
        return success
        
    def move_wrist(self, angle: int) -> bool:
        """Move wrist servo to specified angle."""
        if not self._is_safe_angle('W', angle):
            raise ValueError(f"Angle {angle} is outside safe range {self.SERVO_LIMITS['W']}")
        success = self._send_command('W', angle)
        if success:
            self.current_positions['W'] = angle
        return success
    
    def reset_all(self) -> None:
        """Reset all servos to their middle position (90 degrees)."""
        for servo, (min_angle, max_angle) in self.SERVO_LIMITS.items():
            mid_angle = (min_angle + max_angle) // 2
            self._send_command(servo, mid_angle)
            self.current_positions[servo] = mid_angle
            
    def close(self) -> None:
        """Close the serial connection."""
        self.reset_all()  # Return to safe position before closing
        time.sleep(0.5)   # Wait for movement to complete
        self.serial.close()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 