from flask import jsonify, request
import pykos
import grpc

class RobotController:
    def __init__(self, robot_ip: str = '192.168.42.1'):
        """Initialize robot controller
        
        Args:
            robot_ip: IP address of the KOS robot
            
        Raises:
            ConnectionError: If cannot connect to robot
        """
        try:
            self.kos = pykos.KOS(ip=robot_ip)
            # Test connection by getting actuator state
            self.kos.actuator.get_actuators_state([13])
        except grpc.RpcError as e:
            raise ConnectionError(f"Failed to connect to robot at {robot_ip}: {e.details()}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to robot at {robot_ip}: {str(e)}")
            
        # Configure actuators
        self._configure_actuators()
    
    def _configure_actuators(self):
        """Configure the wrist and pincer actuators"""
        try:
            # Configure wrist
            self.kos.actuator.configure_actuator(
                actuator_id=13,  # wrist
                torque_enabled=True,
                kp=120,
                kd=10
            )
            
            # Configure pincer
            self.kos.actuator.configure_actuator(
                actuator_id=14,  # pincer
                torque_enabled=True,
                kp=120,
                kd=10
            )
        except Exception as e:
            raise RuntimeError(f"Failed to configure actuators: {str(e)}")
    
    def move_robot(self):
        """Handle robot movement requests
        
        Expected JSON format:
        {
            "joints": [
                {"id": 13, "position": 0.5},  # Wrist joint
                {"id": 14, "position": 0.0}   # Pincer
            ]
        }
        """
        # Handle preflight requests
        if request.method == 'OPTIONS':
            response = request.make_default_options_response()
            return response
            
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        try:
            data = request.get_json()
            
            # Validate input format
            if 'joints' not in data:
                return jsonify({"error": "Missing 'joints' field"}), 400
                
            # Validate each joint command
            for joint in data['joints']:
                if 'id' not in joint or 'position' not in joint:
                    return jsonify({"error": "Each joint must have 'id' and 'position'"}), 400
                
                # Validate joint IDs (only allow wrist and pincer)
                if joint['id'] not in [13, 14]:  # wrist and pincer IDs
                    return jsonify({"error": f"Invalid joint ID {joint['id']}. Only wrist (13) and pincer (14) allowed"}), 400
            
            # Send commands to robot
            try:
                response = self.kos.actuator.command_actuators(data['joints'])
                
                # Check if all commands were successful
                success = all(result.success for result in response.results)
                if success:
                    return jsonify({
                        "status": "success",
                        "message": "Robot movement completed"
                    }), 200
                else:
                    # Get error messages for failed commands
                    errors = [f"Joint {result.actuator_id}: {result.error}" 
                             for result in response.results if not result.success]
                    return jsonify({
                        "status": "error",
                        "message": "Some joint commands failed",
                        "errors": errors
                    }), 400
                    
            except grpc.RpcError as e:
                return jsonify({
                    "status": "error",
                    "message": f"Robot communication error: {e.details()}"
                }), 500
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": f"Robot communication error: {str(e)}"
                }), 500
                
        except Exception as e:
            return jsonify({"error": str(e)}), 400 