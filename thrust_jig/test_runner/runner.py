from typing import Optional, List, Dict
from dataclasses import dataclass, field
from pathlib import Path
from os import PathLike
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import configparser
import warnings


config = configparser.ConfigParser()
config.read("runner.ini")

SERIAL_BAUD = 921600
INDEX_MAP = {
    "time_ms": 0,
    "top_motor_rpm": 1,
    "bottom_motor_rpm": 2,
    "batt_voltage_V": 3,
    "batt_current_A": 4,
    "top_current_A": 5,
    "bottom_current_A": 6,
    "thrust_N": 7,
    "torque_N": 8,
}
CONVERSION_MAP = {
    "time_ms": lambda x: x / 1000,  # Convert to ms
    "top_motor_rpm": lambda x: x,
    "bottom_motor_rpm": lambda x: x,
    "batt_voltage_V": lambda x: x,
    "batt_current_A": lambda x: x,
    "top_current_A": lambda x: x,
    "bottom_current_A": lambda x: x,
    "thrust_N": lambda x: x,
    "torque_N": lambda x: x,
}
LABEL_MAP = {
    "time_ms": "Time (ms)",
    "top_motor_rpm": "Top Motor Speed (rpm)",
    "bottom_motor_rpm": "Bottom Motor Speed (rpm)",
    "batt_voltage_V": "Battery Voltage (V)",
    "batt_current_A": "Battery Current (A)",
    "top_current_A": "Top Motor Current (A)",
    "bottom_current_A": "Bottom Motor Current (A)",
    "thrust_N": "Thrust (N)",
    "torque_N": "Torque (N)",
}
INV_LABEL_MAP = {v: k for k, v in LABEL_MAP.items()}


@dataclass(frozen=True)
class TestStep:
    duration_ms: int
    top_throttle: Optional[float] = None
    bottom_throttle: Optional[float] = None
    pitch_angle: Optional[float] = None
    roll_angle: Optional[float] = None


@dataclass(frozen=True)
class TestCommand:
    time_ms: float
    duration_ms: float
    top_throttle: float
    bottom_throttle: float
    pitch_angle: float
    roll_angle: float

    @staticmethod
    def next(step: TestStep, last: "TestCommand") -> "TestCommand":
        return TestCommand(
            time_ms=last.time_ms + last.duration_ms,
            duration_ms=step.duration_ms,
            top_throttle=step.top_throttle
            if step.top_throttle is not None
            else last.top_throttle,
            bottom_throttle=step.bottom_throttle
            if step.bottom_throttle is not None
            else last.bottom_throttle,
            pitch_angle=step.pitch_angle
            if step.pitch_angle is not None
            else last.pitch_angle,
            roll_angle=step.roll_angle
            if step.roll_angle is not None
            else last.roll_angle,
        )


@dataclass(frozen=True)
class TestPlan:
    name: str
    steps: List[TestStep]

    def commands(self, teardown=True) -> List[TestCommand]:
        commands = [
            TestCommand(
                time_ms=0,
                duration_ms=0,
                top_throttle=0,
                bottom_throttle=0,
                pitch_angle=0,
                roll_angle=0,
            )
        ]

        for step in self.steps:
            commands.append(TestCommand.next(step=step, last=commands[-1]))

        if teardown:
            while commands[-1].top_throttle != 0 or commands[-1].bottom_throttle != 0:
                last_top = commands[-1].top_throttle
                last_bottom = commands[-1].bottom_throttle
                next_top = max(0, last_top - 1)
                next_bottom = max(0, last_bottom - 1)
                commands.append(
                    TestCommand.next(
                        step=TestStep(
                            duration_ms=20,
                            top_throttle=next_top,
                            bottom_throttle=next_bottom,
                        ),
                        last=commands[-1],
                    )
                )

        return commands


@dataclass(frozen=True)
class TestDataBuilder:
    data: Dict[str, List[float]] = field(default_factory=dict)

    def add_datapoint(self, key: str, value: float) -> None:
        if key in self.data:
            self.data[key].append(value)
        else:
            self.data[key] = [value]

    def frozen(self) -> pd.DataFrame:
        return pd.DataFrame(self.data).set_index("time_ms")


def available_ports() -> List[Optional[str]]:
    return [port.device for port in serial.tools.list_ports.comports()]


def test_run(
    filename: Optional[str | PathLike[str]],
    plan: Optional[TestPlan] = None,
    teardown=True,
    port: Optional[str] = None,
    timeout: Optional[float] = None,
) -> pd.DataFrame:
    if filename is not None:
        filename = Path(filename)
        if filename.exists():
            print("Loading saved data")
            return (
                pd.read_csv(filename, index_col="Time (ms)")
                .rename(columns=INV_LABEL_MAP)
                .rename_axis("time_ms")
            )
    if plan is None:
        raise ValueError(
            "File does not exist and no test plan was provided to run a new test"
        )
    if port is None:
        port = config.get("Runner", "port", fallback=None)
        if port is None:
            raise ValueError(
                "Could not find a runner.ini config file. Create one in the format of runner.example.ini or specify the 'port' parameter"
            )
    if timeout is None:
        timeout = config.getfloat("Runner", "timeout", fallback=0.1)

    test_data_builder = TestDataBuilder()

    with serial.Serial(port=port, baudrate=SERIAL_BAUD, timeout=timeout) as ser:
        print("Tx: Begin new test spec")
        ser.write(b"Begin new test spec\n")
        print(f'FAIL Rx: {ser.readline().decode(errors="backslashreplace")}')
        print("Tx: time_ms,top_throttle,bottom_throttle,pitch_us,roll_us")
        ser.write(b"time_ms,top_throttle,bottom_throttle,pitch_us,roll_us\n")
        print(f'FAIL Rx: {ser.readline().decode(errors="backslashreplace")}')

        for command in plan.commands(teardown=teardown):
            command_line = f"{command.time_ms},{command.top_throttle},{command.bottom_throttle},{command.pitch_angle},{command.roll_angle}\n"
            ser.write((command_line).encode("utf-8"))

        print(f'FAIL Rx: {ser.readline().decode(errors="backslashreplace")}')
        ser.write(b"Run test\n")
        print("Arming...")
        print(f'FAIL Rx: {ser.readline().decode(errors="backslashreplace")}')
        ctrl_msgs = (
            "",
            "Thrust Jig Firmware Program\r\n",
            "Setting up\r\n",
            "Ready to load test spec\r\n",
            "Starting test\r\n",
            "time_us,top_rpm,bot_rpm,v_bat,i_bat,i_top,i_bot,thrust_N,torque_Nm\r\n",
        )

        print("Running test...")
        while True:
            rx_data = ser.readline().decode(errors="backslashreplace")
            print(f"Rx: {rx_data}")
            if rx_data in ctrl_msgs:
                print("Skipped rx")
                continue
            if "Stopped" in rx_data:
                break

            values = rx_data.split(",")
            for datapoint_key, datapoint_idx in INDEX_MAP.items():
                value = float(values[datapoint_idx])
                value = CONVERSION_MAP[datapoint_key](value)
                test_data_builder.add_datapoint(key=datapoint_key, value=value)

        print("Test complete.")
        test_data = test_data_builder.frozen()
        if filename is not None:
            try:
                test_data.rename(columns=LABEL_MAP).rename_axis("Time (ms)").to_csv(
                    filename
                )
                print("Saved to file")
            except Exception as e:
                warnings.warn(
                    f"File save failed. Test data must be saved manually. Captured exception: {e}"
                )
        return test_data


if __name__ == "__main__":
    print(f"Serial ports: {available_ports()}")

    steps = [
        TestStep(bottom_throttle=throttle, duration_ms=100) for throttle in range(0, 20)
    ]
    plan = TestPlan(
        "test",
        steps=steps,
    )

    data = test_run(filename=None, plan=plan, port="/dev/ttyUSB0")
    data.plot(y="bottom_motor_rpm")
    data.to_csv("test_csv.csv")
