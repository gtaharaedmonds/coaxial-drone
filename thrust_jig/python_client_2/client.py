from typing import Optional, List
from dataclasses import dataclass
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt


SERIAL_BAUD = 115200


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
    plan: List[TestStep]

    def commands(self) -> List[TestCommand]:
        commands = [
            TestCommand(
                time_ms=0,
                duration_ms=2000,
                top_throttle=0,
                bottom_throttle=0,
                pitch_angle=0,
                roll_angle=0,
            )
        ]

        for step in self.plan:
            commands.append(TestCommand.next(step=step, last=commands[-1]))

        return commands


class TestRunner:
    def __init__(self, port: str, timeout=10):
        self.port = port
        self.timeout = timeout

    def run(self, plan: TestPlan):
        with serial.Serial(
            port=self.port, baudrate=SERIAL_BAUD, timeout=self.timeout
        ) as ser:
            # Send start command
            for command in plan.commands():
                # TODO: Encode
                ser.write(("Hello world!" + "\n").encode("utf-8"))
            # Send end command

            # Wait for confirmation

            while True:
                rx_bytes = ser.readline()

                # TODO: Decode and log data
                # Write to CSV file

    @staticmethod
    def plot():
        # Nicely configurable plotting
        plt.figure(figsize=(10, 10))
        plt.plot([0, 1], [0, 1])
        plt.show()
