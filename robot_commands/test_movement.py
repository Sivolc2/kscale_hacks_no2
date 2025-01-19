import grpc
import pytest

import pykos

ACTUATOR_NAME_TO_ID = {
    "left_shoulder_yaw": 11,
    "left_shoulder_pitch": 12,
    "left_elbow_yaw": 13,
    "left_gripper": 14,
    "right_shoulder_yaw": 21,
    "right_shoulder_pitch": 22,
    "right_elbow_yaw": 23,
    "right_gripper": 24,
    "left_hip_yaw": 31,
    "left_hip_roll": 32,
    "left_hip_pitch": 33,
    "left_knee_pitch": 34,
    "left_ankle_pitch": 35,
    "right_hip_yaw": 41,
    "right_hip_roll": 42,
    "right_hip_pitch": 43,
    "right_knee_pitch": 44,
    "right_ankle_pitch": 45,
}

ACTUATOR_ID_TO_NAME = {v: k for k, v in ACTUATOR_NAME_TO_ID.items()}

def main():
    # if not is_server_running(""):
    #     pytest.skip("No active gRPC server at 127.0.0.1:50051")
    client = pykos.KOS(ip='0.0.0.0', port=50051)

    # Tests configuring the actuator.
    actuator_response = client.actuator.configure_actuator(actuator_id=1)
    assert actuator_response.success, f"Actuator response: {actuator_response}"

    # Tests getting the actuator state.
    actuator_state = client.actuator.get_actuators_state(actuator_ids=[1])
    assert actuator_state.states[0].actuator_id == 1, f"Actuator state: {actuator_state}"

    # Tests the IMU endpoints.
    imu_response = client.imu.get_imu_values()
    assert imu_response.accel_x is not None, f"IMU response: {imu_response}"
    client.imu.get_imu_advanced_values()
    client.imu.get_euler_angles()
    client.imu.get_quaternion()
    client.imu.calibrate()
    zero_response = client.imu.zero(duration=1.0, max_retries=1, max_angular_error=1.0)
    assert zero_response.success, f"Zero response: {zero_response}"

    # Tests the K-Clip endpoints.
    start_kclip_response = client.process_manager.start_kclip(action="start")
    assert start_kclip_response.clip_uuid is not None, f"Start K-Clip response: {start_kclip_response}"
    stop_kclip_response = client.process_manager.stop_kclip()
    assert stop_kclip_response.clip_uuid is not None, f"Stop K-Clip response: {stop_kclip_response}"


def main2():
    # Change IP to localhost
    # client = pykos.KOS(ip='10.33.11.192')
    client = pykos.KOS(ip='192.168.42.1')

    # while True:
    #     # Get basic IMU sensor values
    #     imu_values = client.imu.get_imu_values()
    #     print(f"Accelerometer X: {imu_values.accel_x}")
    #     print(f"Gyroscope Z: {imu_values.gyro_z}")
    #     import time
    #     time.sleep(1)


    # matrix_info = client.led_matrix.get_matrix_info()
    # print(f"Matrix size: {matrix_info.width} x {matrix_info.height}")

    client.actuator.configure_actuator(actuator_id=11, torque_enabled=True)
    client.actuator.configure_actuator(actuator_id=12, torque_enabled=True)

    commands = [
        {"actuator_id": 11, "position": -0.0},
        {"actuator_id": 12, "position": 0.0}
    ]
    response = client.actuator.command_actuators(commands)


    print(client.actuator.get_actuators_state([12]))
    breakpoint()

    # Configure actuator with ID 1
    # response = client.actuator.configure_actuator(
    #     actuator_id=1,
    #     kp=32,
    #     kd=32,
    #     ki=32,
    #     max_torque=100.0,
    #     torque_enabled=True,
    #     zero_position=True
    # )
    # if response.success:
    #     print("Actuator configured successfully.")
    # else:
    #     print(f"Failed to configure actuator: {response.error}")
    
    # # Command multiple actuators
    # commands = [
    #     {"actuator_id": 1, "position": 90.0},
    #     {"actuator_id": 2, "position": 180.0}
    # ]
    # response = client.actuator.command_actuators(commands)
    # for result in response.results:
    #     if result.success:
    #         print(f"Actuator {result.actuator_id} commanded successfully.")
    #     else:
    #         print(f"Failed to command actuator {result.actuator_id}: {result.error}")

    

def is_server_running(address: str) -> bool:
    try:
        channel = grpc.insecure_channel(address)
        grpc.channel_ready_future(channel).result(timeout=1)
        return True
    except grpc.FutureTimeoutError:
        return False
    
if __name__ == "__main__":
    main2()
