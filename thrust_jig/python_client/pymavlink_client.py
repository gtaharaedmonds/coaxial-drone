import pymavlink.mavutil
import time

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pymavlink.mavutil.mavlink # pyright: reportMissingModuleSource = false

# drone = mavutil.mavlink_connection('COM6', baud=57600)
drone = pymavlink.mavutil.mavlink_connection('udpin:0.0.0.0:14551')

# Wait for drone to connect
drone.wait_heartbeat()
print('Connected')

def throttle_sweep(max_throttle=1):
    test_length = 50
    steps = 10
    frequency = 20
    for i in range(int(steps * max_throttle)):
        throttle = (i + 1) / steps
        print(f'Throttle: {throttle}')
        for _ in range(frequency * test_length // steps):
            drone.mav.manual_control_send(
                target=drone.target_system,
                x=0, y=0, z=throttle*1000, r=0,
                buttons=0
            )
            time.sleep(1/frequency)

def vane_sweep(max_deflection=1):
    test_length = 50
    steps = 10
    frequency = 20
    for i in range(int(steps * max_deflection)):
        throttle = (i + 1) / steps
        print(f'Deflection: {throttle}')
        for _ in range(frequency * test_length // steps):
            drone.mav.manual_control_send(
                target=drone.target_system,
                x=0, y=-throttle*1000, z=500, r=0,
                buttons=0
            )
            time.sleep(1/frequency)

# Set ACRO mode
mode_map = drone.mode_mapping()
if mode_map is None or 'ACRO' not in mode_map:
    raise Exception('Drone does not support ACRO mode')

drone.set_mode_apm(mode_map['ACRO'])
print('Setting ACRO mode')
while True:
    # Wait for ACK command
    # Would be good to add mechanism to avoid endlessly blocking
    # if the autopilot sends a NACK or never receives the message
    ack_msg = drone.recv_match(type='COMMAND_ACK', blocking=True)
    ack_msg = ack_msg.to_dict()

    # Continue waiting if the acknowledged command is not `set_mode`
    if ack_msg['command'] != pymavlink.mavutil.mavlink.MAV_CMD_DO_SET_MODE:
        continue

    # Print the ACK result !
    print(pymavlink.mavutil.mavlink.enums['MAV_RESULT'][ack_msg['result']].description)
    break

# Run test
drone.arducopter_arm()
print('Arming')
drone.motors_armed_wait()
print('Motors armed')
throttle_sweep()
print('Running throttle sweep')
drone.arducopter_disarm()
print('Disarming')
drone.motors_disarmed_wait()
print('Disarmed')