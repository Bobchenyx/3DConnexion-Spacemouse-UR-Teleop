# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

Install system dependencies:
```bash
sudo apt install libspnav-dev spacenavd
sudo systemctl start spacenavd
```

Create and activate the project conda environment:
```bash
conda create -n spacemouse-ur python=3.12
conda activate spacemouse-ur
pip install ur_rtde
pip install spnav --no-build-isolation
pip install numpy
```

**Known spnav issue:** `PyCObject_AsVoidPtr` is deprecated. After installing spnav, fix it:
```bash
# Find the installed file
SPNAV_PATH=$(python -c "import spnav; import os; print(os.path.dirname(spnav.__file__))")/\_\_init\_\_.py
sed -i 's/PyCObject_AsVoidPtr/PyCapsule_GetPointer/g' $SPNAV_PATH
```
On this machine the fix has already been applied to both `base` and `spacemouse-ur` environments.

## Running

```bash
conda activate spacemouse-ur

# UR3 teleoperation (current main script)
python3 3DConnexion_UR3_Teleop.py
```

Stop with `Ctrl+C` — this triggers graceful shutdown (stops RTDE script and SpaceMouse thread).

Reference scripts for UR5 and gripper control are in `reference/`.

### Diagnostic scripts (`scripts/`)

```bash
# Raw spnav values only — minimal, no processing
python3 scripts/check_spacemouse_raw.py

# Raw + processed (deadzone-filtered, coordinate-transformed) — matches teleop behavior
python3 scripts/check_spacemouse.py
```

Both scripts print at 10Hz max and stop printing when the device is idle.

```bash
# Check UR3 connection and status; if ready, optionally move to home position
python3 scripts/check_robot.py

# Move to home position directly (run after check passes)
python3 scripts/init_robot.py
```

Home position: `[0°, -90°, 90°, -90°, -90°, 0°]` — all joints at multiples of 90°.

## Architecture

The system has three layers:

**SpaceMouse input** (`Spacemouse` class, a `Thread`): Polls `spnav` events at 200Hz and stores the latest `SpnavMotionEvent` and button states. The `get_motion_state_transformed()` method applies a coordinate frame rotation (`tx_zup_spnav`) to convert from SpaceMouse frame to robot frame and scales by `SCALE_FACTOR`. Deadzone is configured via the `deadzone=` constructor parameter (unified in one place); the hardcoded per-axis deadzone in `get_motion_state_transformed()` has been removed.

**Robot control** (RTDE): Uses `ur_rtde` to send Cartesian velocity commands (`speedL`) at 100Hz to the robot. Requires robot to be in mode 7 (running). Robot IP is hardcoded as `ROBOT_HOST = "192.168.0.2"`.

**Gripper control** (`reference/robotiq_gripper.py`): Not currently in use. When connected, communicates with Robotiq HAND-E via TCP socket on port 63352. Two reference modes exist in `reference/`: button open/close, or incremental position control (0–255).

## Key Parameters

| Parameter | Location | Value |
|-----------|----------|-------|
| `ROBOT_HOST` | `3DConnexion_UR3_Teleop.py` | `192.168.0.2` |
| `SCALE_FACTOR` | `3DConnexion_UR3_Teleop.py` | `0.1` |
| `acceleration` | `3DConnexion_UR3_Teleop.py` | `0.5` |
| `max_value` | `Spacemouse.__init__` | `300` (wired); use `500` for wireless SpaceMouse |
| `deadzone` | `Spacemouse.__init__` (`deadzone=`) | `0.2` — scalar applies to all 6 axes; pass a 6-tuple for per-axis control |
| `speedL time` | `main()` | `0.1` s safety timeout: robot decelerates and stops if no new command arrives within this window |
| Control loop rate | `main()` | 100Hz (`time.sleep(1/100)`) |

## Lab Hardware Configuration

- **Robot**: Universal Robots UR3
- **Input device**: 3DConnexion SpaceMouse (wired, `max_value=300`)
- **Gripper**: Not installed — all gripper code is commented out with `[OPTIONAL - Robotiq Gripper]` markers
- **Robot IP**: `192.168.0.2`
- **Network**: Workstation and UR3 must be on the same subnet

Before running, verify connectivity and enable Remote Control on the UR3 teach pendant.

## RS485 Gripper (`gripper/`)

A separate subdirectory for an RS485-based industrial gripper connected via USB-to-RS485 adapter. See `gripper/CLAUDE.md` for details. Requires `pip install pyserial` and `sudo chmod 666 /dev/ttyUSB0`.

## Import Quirk

The main script filename (`3DConnexion_UR3_Teleop.py`) starts with a digit, so Python cannot import it with a normal `import` statement. The diagnostic scripts in `scripts/` work around this using `importlib.util.spec_from_file_location` to load the `Spacemouse` class directly from the file path.
