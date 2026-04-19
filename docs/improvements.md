---
title: Areas for Improvement
description: Limitations, future work, and follow-up tasks.
---

## 🔗 Navigation

- [Home](index.md)
- [Requirements Specification](requirements-specification.md)
- [Concept of Operations](con-ops.md)
- [High Level Design](high-level-design.md)
- [Software Subsystem: Navigation and FSM](subsystem-nav-fsm.md)
- [Software Subsystem: ArUco Marker Detection](subsystem-software-aruco.md)
- [Mechanical Subsystem](subsystem-mechanical.md)
- [Electrical Subsystem](subsystem-electrical.md)
- [Interface Control Document](interface-control-document.md)
- [Software and Firmware Development](software-firmware-development.md)
- [Testing Documentation](testing-documentation.md)
- [User Manual](user-manual.md)
- [Areas for Improvement](improvements.md)
- [Appendix](appendix.md)

---

# Areas for Improvement

## 1. Launcher subsystem performance issues

Issue:
Both launcher servos stopped working on the mission day and later revived unexpectedly, but no longer followed the expected timing sequence. Troubleshooting focused on isolating the fault to `shooter_controller.py` logic versus faulty PWM wiring, because servo motion became erratic and desynchronized. The issue remains unresolved; the current leading suspicion is a logic level shifter fault.

Improvement:
- Replace the logic level shifter and re-run timing validation tests.
- Re-verify PWM wiring integrity and connector stability under motion.
- Run isolated bench tests on launcher timing before full mission integration.

## 2. Map message drops

Issue:
The map loads on first boot but often stops loading on second boot. This behavior suggests a camera-process-related overload path where duplicate nodes and camera processes overwhelm the data stream to the laptop, preventing SLAM Toolbox from receiving stable map data. This was mitigated by running the cleanup scripts documented in software and firmware setup. LiDAR QoS was also adjusted to reliable.

Improvement:
- Enforce cleanup script execution before every run as a standard operating step.
- Add automated pre-launch checks for duplicate nodes and camera processes.
- Continue QoS tuning for LiDAR and map-related topics under hardware load.

## 3. Hardware-level uncertainty on OpenCR board

Issue:
Intermittent TF and odometry message drops were observed on real hardware, with message frequencies below healthy operating range. Map updates are also significantly slower than expected, and odometry data takes much longer to refresh than normal. This suggests a potential OpenCR-related hardware bottleneck or communication instability, but root cause is not yet fully verified.

Improvement:
- Run controlled diagnostics to compare OpenCR serial behavior across power levels and cable conditions.
- Log TF/odom frequency baselines and define hard restart thresholds in operations.
- Prepare a hardware replacement/verification path to confirm or eliminate OpenCR as the root cause.
