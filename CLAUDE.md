# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

Install system dependencies and Python packages:
```bash
sudo apt install libspnav-dev spacenavd
sudo systemctl start spacenavd
pip install spnav ur_rtde
```

**Known spnav issue:** `PyCObject_AsVoidPtr` is deprecated. Find the spnav package (`find . -name "spnav"`) and replace all instances of `PyCObject_AsVoidPtr` with `PyCapsule_GetPointer` in `__init__.py`.

## Running

```bash
# UR3 teleoperation (current main script)
python3 3DConnexion_UR3_Teleop.py
```

Stop with `Ctrl+C` — this triggers graceful shutdown (stops RTDE script and SpaceMouse thread).

Reference scripts for UR5 and gripper control are in `reference/`.

## Architecture

The system has three layers:

**SpaceMouse input** (`Spacemouse` class, a `Thread`): Polls `spnav` events at 200Hz and stores the latest `SpnavMotionEvent` and button states. The `get_motion_state_transformed()` method applies a coordinate frame rotation (`tx_zup_spnav`) to convert from SpaceMouse frame to robot frame, applies a 0.3 deadzone, and scales by `SCALE_FACTOR`.

**Robot control** (RTDE): Uses `ur_rtde` to send Cartesian velocity commands (`speedL`) at 100Hz to the robot. Requires robot to be in mode 7 (running). Robot IP is hardcoded as `ROBOT_HOST = "192.168.0.2"`.

**Gripper control** (`robotiq_gripper.py`, `RobotiqGripper` class): Communicates with Robotiq HAND-E gripper via TCP socket on port 63352. Uses string-based SET/GET protocol. `activate()` resets and re-activates the gripper with auto-calibration to determine actual min/max positions.

**Gripper control** (`reference/robotiq_gripper.py`): Not currently in use. When connected, communicates with Robotiq HAND-E via TCP socket on port 63352. Two reference modes exist in `reference/`: button open/close, or incremental position control (0–255).

## Key Parameters

| Parameter | Location | Value |
|-----------|----------|-------|
| `ROBOT_HOST` | Both teleop scripts | `192.168.0.2` |
| `SCALE_FACTOR` | Both teleop scripts | `0.3` |
| `max_value` | `Spacemouse.__init__` | `300` (wired, current hardware) |
| Deadzone threshold | `get_motion_state_transformed` | `0.3` |
| Control loop rate | `main()` | 100Hz (`time.sleep(1/100)`) |

## Lab Hardware Configuration

- **Robot**: Universal Robots UR3
- **Input device**: 3DConnexion SpaceMouse (wired, `max_value=300`)
- **Gripper**: Not installed — all gripper code is commented out with `[OPTIONAL - Robotiq Gripper]` markers
- **Robot IP**: `192.168.0.2`
- **Network**: Workstation and UR3 must be on the same subnet

Before running, verify connectivity and enable Remote Control on the UR3 teach pendant.
