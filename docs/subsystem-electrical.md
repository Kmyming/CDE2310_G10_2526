---
title: Electrical Subsystem
description: Power, wiring, and actuator integration.
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

# Electrical Subsystem

## Purpose

Capture the project’s power distribution, wiring, and electrical integration strategy.

## Power Budget

- List the expected loads.
- Capture nominal voltage and current assumptions.
- Reserve margin for sensor and actuation peaks.

## Wiring and Connections

- Document the robot-side wiring paths.
- Note signal-level conversion if used.

## Sensor and Actuator Integration

- Camera power and data.
- Shooter and docking control interfaces.

## Voltage and Current Assumptions

- State the design assumptions used in the budget.

## Safety Considerations

- Protect against overcurrent and incorrect polarity.
- Keep hardware actuation disabled unless explicitly requested.

## Validation

- Confirm that the electrical design supports the intended runtime behavior.
