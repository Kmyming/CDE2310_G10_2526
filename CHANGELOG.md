## [0.1.0](https://github.com/Kmyming/CDE2310_G10_2526/pull/17) - 2026-03-26

Refactored the FSM state machine logic, removing obsolete components, improving state transition reliability, and enhancing overall mission control clarity.

### Added / Changed
- feat(fsm): Increased the `required_markers` count from 2 to 3 in `FSM/fsm_code.py`.
- feat(fsm): Improved logging messages for state transitions and added type hints for callback functions in `FSM/fsm_code.py`.

### Fixed
- fix(fsm): Removed unused `PoseStamped` import, `current_marker_pub` publisher, and `aruco_pose` subscriber from `FSM/fsm_code.py`.
- fix(fsm): Refined the `EXPLORE` state logic in `FSM/fsm_code.py` to correctly transition to `DOCK` or `END`, removing a redundant `self.change_state("EXPLORE")` call.
- fix(fsm): Added `self.timer.cancel()` in the `END` state of `FSM/fsm_code.py` to stop the state machine loop and prevent continuous logging after mission completion.