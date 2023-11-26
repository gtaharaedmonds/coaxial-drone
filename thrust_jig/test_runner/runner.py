from typing import Optional, List
from dataclasses import dataclass
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
import numpy as np
import csv


SERIAL_BAUD = 115200
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


class TestRunner:
    def __init__(self, port: str, timeout=10):
        self.port = port
        self.timeout = timeout
        self.data = {}

    @staticmethod
    def available_ports() -> List[Optional[str]]:
        return [port.device for port in serial.tools.list_ports.comports()]

    @staticmethod
    def keys() -> List[str]:
        return list(INDEX_MAP.keys())

    def run(self, plan: TestPlan, teardown=True):
        self.data = {}

        with serial.Serial(
            port=self.port, baudrate=SERIAL_BAUD, timeout=self.timeout
        ) as ser:
            ser.write(b"Begin new test spec\n")
            ser.write(b"time_ms,top_throttle,bottom_throttle,pitch_us,roll_us\n")
            ser.write(b"Begin new test spec\n")

            for command in plan.commands(teardown=teardown):
                command_line = f"{command.time_ms},{command.top_throttle},{command.bottom_throttle},{command.pitch_angle},{command.roll_angle}\n"
                ser.write((command_line).encode("utf-8"))

            ser.write(b"Run test\n")
            print("Arming...")
            ser.readline().decode()
            ser.readline().decode()

            print("Running test...")
            while True:
                rx_data = ser.readline().decode()
                if "Stopped" in rx_data:
                    break

                values = rx_data.split(",")
                for datapoint_key, datapoint_idx in INDEX_MAP.items():
                    value = float(values[datapoint_idx])
                    value = CONVERSION_MAP[datapoint_key](value)

                    if datapoint_key in self.data:
                        self.data[datapoint_key].append(value)
                    else:
                        self.data[datapoint_key] = [value]

            print("Test complete.")

    def plot(
        self,
        key: str,
        tmin: Optional[int] = None,
        tmax: Optional[int] = None,
        *args,
        **kwargs,
    ) -> None:
        time = self.values("time_ms", tmin=tmin, tmax=tmax)
        values = self.values(key, tmin=tmin, tmax=tmax)

        plt.figure(figsize=(6, 6))
        plt.plot(time, values, *args, **kwargs)
        plt.xlabel(LABEL_MAP["time_ms"])
        plt.ylabel(LABEL_MAP[key])
        plt.show()

    def save(self, path: str) -> None:
        with open(path, "w") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([LABEL_MAP[key] for key in self.data.keys()])
            writer.writerows(zip(*self.data.values()))

    def values(
        self, key: str, tmin: Optional[float] = None, tmax: Optional[float] = None
    ) -> np.ndarray:
        # Find bounds for t_min.
        time = np.array(self.data["time_ms"])

        imin = 0
        if tmin is not None:
            for i, t in enumerate(time):
                if t > tmin:
                    imin = i
                    break

        # Find bounds for t_max.
        imax = len(time)
        if tmax is not None:
            for i, t in enumerate(time):
                if t > tmax:
                    imax = i
                    break

        values = self.data[key][imin:imax]
        return np.array(values)


if __name__ == "__main__":
    print(f"Serial ports: {TestRunner.available_ports()}")

    steps = [
        TestStep(bottom_throttle=throttle, duration_ms=100) for throttle in range(0, 20)
    ]
    plan = TestPlan(
        "test",
        steps=steps,
    )

    runner = TestRunner(port="/dev/ttyUSB0")
    runner.run(plan=plan)
    runner.plot("bottom_motor_rpm")
    runner.save("test_csv.csv")
