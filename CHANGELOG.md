## 1.1.0 - 2026-04-07

### Added / Changed
- feat(Docking): Implemented a new ArUco-based docking feature in `Docker/Aruco_Docker_Final.py`, including a state machine for approach, side-stepping, obstacle avoidance, and a special search mode.
- feat(shooting): Added `set_servo_angle` method in `Shooter/Payload_Delivery.py` for precise PWM control of the gate servo.

### Fixed
- fix(servo): Corrected gate opening and closing logic in `Shooter/Payload_Delivery.py` to utilize the new PWM-based `set_servo_angle` method.
- fix(Pose_publisher): Updated `Marker/Pose_publisher_V2_TF2.py` to correctly detect ArUco markers using `cv2.aruco.DICT_4X4_250`.