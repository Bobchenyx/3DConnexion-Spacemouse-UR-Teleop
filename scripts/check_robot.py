#!/usr/bin/env python3
"""Check UR3 connection and status. Does not move the robot."""

import sys
from rtde_receive import RTDEReceiveInterface

ROBOT_HOST = "192.168.0.2"

ROBOT_MODES = {
    -1: "NO_CONTROLLER",
     0: "DISCONNECTED",
     1: "CONFIRM_SAFETY",
     2: "BOOTING",
     3: "POWER_OFF",
     4: "POWER_ON",
     5: "IDLE",
     6: "BACKDRIVE",
     7: "RUNNING",
}

print(f"Connecting to UR3 at {ROBOT_HOST}...")
try:
    rtde_r = RTDEReceiveInterface(ROBOT_HOST)
except Exception as e:
    print(f"Connection failed: {e}")
    sys.exit(1)

print("Connected.\n")

mode = rtde_r.getRobotMode()
mode_name = ROBOT_MODES.get(mode, "UNKNOWN")
ready = "OK — ready for teleoperation" if mode == 7 else "NOT ready (mode must be 7 / RUNNING)"

print(f"Robot mode:    {mode} ({mode_name})  →  {ready}")
print(f"TCP position:  {[round(v, 4) for v in rtde_r.getActualTCPPose()]}")
print(f"Joint angles:  {[round(v, 4) for v in rtde_r.getActualQ()]}")
print(f"TCP speed:     {[round(v, 4) for v in rtde_r.getActualTCPSpeed()]}")
