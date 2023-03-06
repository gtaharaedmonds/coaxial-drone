import serial
import serial.tools.list_ports
import csv
from pathlib import Path
from datetime import datetime
import argparse


def connect_to_device(port: str, timeout=10):
    """
    Connect to device on port, throw an error on failure.
    """

    return serial.Serial(port, baudrate=9600, timeout=timeout)


def load_settings(calibration_path: Path):
    """
    Loads most recent calibration file for a given device id

    Returns (channel_names, offsets, scales)
    """

    with calibration_path.open() as calibration_file:
        csv_rows = csv.reader(calibration_file)

        # Skip capture time row
        next(csv_rows)

        # For each of the next rows, ignore the first column and convert datatypes if required
        channel_names = next(csv_rows)[0].split()[1:]
        offsets = [float(offset) for offset in next(csv_rows)[0].split()[1:]]
        scales = [float(scale) for scale in next(csv_rows)[0].split()[1:]]

        return channel_names, offsets, scales, calibration_path


def run_experiment(port: str, experiment_dir: Path, calibration_path: Path):
    """Main program flow"""
    ser = connect_to_device(port)

    channel_names, offsets, scales, calibration_path = load_settings(calibration_path)

    local_tz = datetime.now().astimezone().tzinfo
    file_time = datetime.now(tz=local_tz)
    with open(
        f"{experiment_dir}/{file_time:%Y-%m-%d_%H-%M-%S}.csv", "w", newline=""
    ) as csv_file:
        csv_writer = csv.writer(csv_file)

        # Write file header
        csv_writer.writerow(["calibration_file", calibration_path])
        start_time = datetime.now(tz=local_tz)
        csv_writer.writerow(
            ["start_time", start_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z")]
        )
        csv_writer.writerow([])
        csv_writer.writerow(
            [*channel_names, *(f"{name}_raw" for name in channel_names)]
        )

        # Clear RX buffer
        ser.flush()

        while True:
            line = ser.readline()
            raw_readings = [int(float(reading)) for reading in line.decode().split()]

            calibrated_readings = [
                scale * reading + offset
                for scale, reading, offset in zip(scales, raw_readings, offsets)
            ]

            csv_writer.writerow([*calibrated_readings, *raw_readings])


if __name__ == "__main__":
    available_ports = [port.name for port in serial.tools.list_ports.comports()]

    parser = argparse.ArgumentParser(
        prog="Coax Drone Force Measurement Interface",
        description="Reads data from load cells in the force measurement jig",
    )
    parser.add_argument(
        "port", metavar="P", help=f"Serial port, found: {available_ports}"
    )
    parser.add_argument(
        "--experiment-dir",
        default="experiments",
        type=Path,
        help="Path to experiment directory",
    )
    parser.add_argument(
        "--calibration-dir",
        default="calibration",
        type=Path,
        help="Path to device calibration/settings directory",
    )
    parser.add_argument(
        "--calibration-name",
        default="config.csv",
        type=str,
        help="Name of the file where configs are stored",
    )
    args = parser.parse_args()

    calibration_path = args.calibration_dir / args.calibration_name
    run_experiment(args.port, args.experiment_dir, calibration_path)
