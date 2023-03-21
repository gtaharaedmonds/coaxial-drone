import pymavlink.mavutil
import time
from datetime import datetime
import csv
from pathlib import Path

from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    import pymavlink.mavutil.mavlink # pyright: reportMissingModuleSource = false

# drone = mavutil.mavlink_connection('COM6', baud=57600, source_system=245)
drone = pymavlink.mavutil.mavlink_connection('udpin:0.0.0.0:14551', source_system=245)

log_dir = Path('test_logs')
local_tz = datetime.now().astimezone().tzinfo
file_time = datetime.now(tz=local_tz)
log_file = open(log_dir / f'{file_time:%Y-%m-%dT%H_%M_%S%z}.csv', 'w', newline='')
csv_writer = csv.writer(log_file)

def enable_motor_passthrough(ccw_enabled=True, cw_enabled=True):
    drone.param_set_send('SYSID_MYGCS', 245, pymavlink.mavutil.mavlink.MAVLINK_TYPE_INT16_T) # set this script as ground control
    drone.param_set_send('SERVO1_FUNCTION', 51, pymavlink.mavutil.mavlink.MAVLINK_TYPE_INT16_T) # roll -> RCIN1
    drone.param_set_send('SERVO2_FUNCTION', 52, pymavlink.mavutil.mavlink.MAVLINK_TYPE_INT16_T) # pitch -> RCIN2
    drone.param_set_send('SERVO5_FUNCTION', 53 if ccw_enabled else 0, pymavlink.mavutil.mavlink.MAVLINK_TYPE_INT16_T) # throttle -> RCIN3
    drone.param_set_send('SERVO6_FUNCTION', 53 if cw_enabled else 0, pymavlink.mavutil.mavlink.MAVLINK_TYPE_INT16_T) # throttle -> RCIN3

def disable_motor_passthrough():
    drone.param_set_send('SYSID_MYGCS', 255, pymavlink.mavutil.mavlink.MAVLINK_TYPE_INT16_T) # set default ground control ID
    drone.param_set_send('SERVO1_FUNCTION', 33, pymavlink.mavutil.mavlink.MAVLINK_TYPE_INT16_T) # roll -> Motor 1
    drone.param_set_send('SERVO2_FUNCTION', 34, pymavlink.mavutil.mavlink.MAVLINK_TYPE_INT16_T) # pitch -> Motor 2
    drone.param_set_send('SERVO5_FUNCTION', 37, pymavlink.mavutil.mavlink.MAVLINK_TYPE_INT16_T) # ccw prop -> Motor 5
    drone.param_set_send('SERVO6_FUNCTION', 38, pymavlink.mavutil.mavlink.MAVLINK_TYPE_INT16_T) # cw prop -> Motor 6

def set_mode(mode: str):
    mode_map = drone.mode_mapping()
    if mode_map is None or mode not in mode_map:
        raise Exception(f'Drone does not support {mode} mode')

    drone.set_mode_apm(mode_map[mode])
    while True:
        # Wait for ACK command
        # Would be good to add mechanism to avoid endlessly blocking
        # if the autopilot sends a NACK or never receives the message
        ack_msg = drone.recv_match(type='COMMAND_ACK', blocking=True)
        ack_msg = ack_msg.to_dict()

        # Continue waiting if the acknowledged command is not `set_mode`
        if ack_msg['command'] != pymavlink.mavutil.mavlink.MAV_CMD_DO_SET_MODE:
            continue
        break

def force_disarm():
    drone.mav.command_long_send(
        drone.target_system,  # target_system
        drone.target_component,
        pymavlink.mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, # command
        0, # confirmation
        0, # param1 (0 to indicate disarm)
        21196, # param2 (force)
        0, # param3
        0, # param4
        0, # param5
        0, # param6
        0) # param7

def get_param(param):
    drone.param_fetch_one(param)
    drone.recv_match(type='PARAM_VALUE', blocking=True)
    return drone.param(param)


def sweep_channel(channel: Literal['x', 'y', 'z', 'r'],
                  start_val: int, end_val: int,
                  x: int | None = None, y: int | None = None,
                  z: int | None = None, r: int | None = None,
                  test_length=50,
                  steps=10,
                  stop_fraction=1,
                  frequency=20):
    """
    Sweep the specified channel in `steps` steps from `start_val` to `end_val`,
    stopping when the test exceeds `stop_fraction` completion. Inputs are repeated at
    `frequency` Hz and the total length of the test when `stop_fraction` is 1 is `test_length` s

    You must specify the values of the channels not being swept on a [-1000, 1000] scale
    """
    for i in range(steps + 1):
        input_fraction = i / steps
        if input_fraction > stop_fraction:
            break
        print(f'{channel} channel input: {input_fraction}')
        input_scaled = int(input_fraction * (end_val - start_val) + start_val)
        csv_writer.writerow([input_scaled, datetime.now(tz=local_tz).strftime('%Y-%m-%dT%H:%M:%S.%f%z')])
        for _ in range(frequency * test_length // steps):
            drone.mav.manual_control_send(
                target=drone.target_system,
                **{'x': x, 'y': y, 'z': z, 'r': r, channel: input_scaled},
                buttons=0
            )
            time.sleep(1/frequency)

def vane_pwm_to_input(pwm: float):
    return int((pwm - 1500) * 2)

def sweep_throttle(**kwargs):
    y = vane_pwm_to_input(get_param('SERVO1_TRIM'))
    x = vane_pwm_to_input(get_param('SERVO2_TRIM'))
    sweep_channel('z', start_val=0, end_val=1000, x=x, y=y, r=0, **kwargs)

def sweep_vane(channel: Literal['x', 'y'], direction: Literal[-1, 1], end_val=None, z=500, **kwargs):
    if direction not in (-1, 1):
        raise ValueError('Direction for vane sweep must be -1 or 1')
    params = {'z': z, 'r': 0}
    if channel == 'x':
        params['start_val'] = vane_pwm_to_input(get_param('SERVO2_TRIM'))
        params['y'] = vane_pwm_to_input(get_param('SERVO1_TRIM'))
        if direction == -1:
            params['end_val'] = vane_pwm_to_input(get_param('SERVO2_MIN'))
        else:
            params['end_val'] = vane_pwm_to_input(get_param('SERVO2_MAX'))
    elif channel == 'y':
        params['start_val'] = vane_pwm_to_input(get_param('SERVO1_TRIM'))
        params['x'] = vane_pwm_to_input(get_param('SERVO2_TRIM'))
        if direction == -1:
            params['end_val'] = vane_pwm_to_input(get_param('SERVO1_MIN'))
        else:
            params['end_val'] = vane_pwm_to_input(get_param('SERVO1_MAX'))
    else:
        raise ValueError('Vane sweep channel must be x or y')

    if end_val is not None:
        params['end_val'] = end_val

    sweep_channel(channel, **params, **kwargs)

def run_manual_test(test_fcn, ccw_enabled=True, cw_enabled=True):
    with log_file:
        csv_writer.writerow(['Start', datetime.now(tz=local_tz).strftime('%Y-%m-%dT%H:%M:%S.%f%z')])
        # Enable manual motor control
        print('Enabling manual motor control')
        enable_motor_passthrough(ccw_enabled=ccw_enabled, cw_enabled=cw_enabled)
        # Set ACRO mode
        print('Setting ACRO mode')
        set_mode('ACRO')
        print('Acro mode set')

        # Run test
        drone.arducopter_arm()
        print('Arming')
        drone.motors_armed_wait()
        print('Motors armed')
        csv_writer.writerow(['Armed', datetime.now(tz=local_tz).strftime('%Y-%m-%dT%H:%M:%S.%f%z')])
        try:
            test_fcn()
        finally:
            force_disarm()
            print('Disarming')
            disable_motor_passthrough()
            print('Disabled manual motor control')
            drone.motors_disarmed_wait()
            print('Disarmed')
            csv_writer.writerow(['Disarmed', datetime.now(tz=local_tz).strftime('%Y-%m-%dT%H:%M:%S.%f%z')])

def run_dual_prop_throttle_sweep():
    run_manual_test(sweep_throttle)

def run_top_prop_throttle_sweep():
    run_manual_test(sweep_throttle, ccw_enabled=False)

def run_bottom_prop_throttle_sweep():
    run_manual_test(sweep_throttle, cw_enabled=False)

def run_roll_vane_sweep():
    run_manual_test(lambda: sweep_vane('y', direction=-1))

# Wait for drone to connect
drone.wait_heartbeat()
print('Connected')

run_roll_vane_sweep()
