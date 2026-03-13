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
# Basic teleoperation (open/close gripper with buttons)
python3 3DConnexion_UR5_Teleop.py

# Teleoperation with continuous gripper position control
python3 3DConnexion_UR5_Teleop_Gripper_Control.py
```

Stop with `Ctrl+C` — this triggers graceful shutdown (stops RTDE script and SpaceMouse thread).

## Architecture

The system has three layers:

**SpaceMouse input** (`Spacemouse` class, a `Thread`): Polls `spnav` events at 200Hz and stores the latest `SpnavMotionEvent` and button states. The `get_motion_state_transformed()` method applies a coordinate frame rotation (`tx_zup_spnav`) to convert from SpaceMouse frame to robot frame, applies a 0.3 deadzone, and scales by `SCALE_FACTOR`.

**Robot control** (RTDE): Uses `ur_rtde` to send Cartesian velocity commands (`speedL`) at 100Hz to the robot. Requires robot to be in mode 7 (running). Robot IP is hardcoded as `ROBOT_HOST = "192.168.20.124"`.

**Gripper control** (`robotiq_gripper.py`, `RobotiqGripper` class): Communicates with Robotiq HAND-E gripper via TCP socket on port 63352. Uses string-based SET/GET protocol. `activate()` resets and re-activates the gripper with auto-calibration to determine actual min/max positions.

**Two gripper control modes:**
- `3DConnexion_UR5_Teleop.py`: Button 0 = fully open, Button 1 = fully closed
- `3DConnexion_UR5_Teleop_Gripper_Control.py`: Buttons increment/decrement `gripper_position` by 3 (range 0–255) for finer control

## Key Parameters

| Parameter | Location | Value |
|-----------|----------|-------|
| `ROBOT_HOST` | Both teleop scripts | `192.168.20.124` |
| `SCALE_FACTOR` | Both teleop scripts | `0.3` |
| `max_value` | `Spacemouse.__init__` | `500` (wireless), `300` (wired) |
| Deadzone threshold | `get_motion_state_transformed` | `0.3` |
| Control loop rate | `main()` | 100Hz (`time.sleep(1/100)`) |
