import serial
import serial.tools.list_ports
import csv
from pathlib import Path
from datetime import datetime
import argparse
import yaml


SERIAL_BAUD = 115200


def load_config(config_path: Path):
    """
    Loads config file from path.

    """
    with open(config_path, "r") as config_file:
        config_data = yaml.safe_load(config_file)

    names = []
    scales = []
    offsets = []
    units = []
    save_raw = []

    for channel in config_data["channels"].values():
        name = channel["name"]
        scale = channel["scale"]
        offset = channel["offset"]
        unit = channel["unit"]

        names.append(name)
        scales.append(scale)
        offsets.append(offset)
        units.append(unit)
        save_raw.append(True if scale != 1 or offset != 0 else False)

    return names, scales, offsets, units, save_raw


def run_experiment(port: str, out_dir: Path, config_path: Path):
    """
    Main program flow.

    """
    # Open connection to the ESP32.
    ser = serial.Serial(port, baudrate=SERIAL_BAUD, timeout=5)

    # Load channels config.
    channel_names, offsets, scales, units, save_raw = load_config(config_path)

    # Get current time for the output CSV name.
    local_tz = datetime.now().astimezone().tzinfo
    file_time = datetime.now(tz=local_tz)
    file_name = f"{file_time:%Y-%m-%d_%H-%M-%S}"

    with open(f"{out_dir}/{file_name}.csv", "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)

        # Write file header.
        csv_writer.writerow(["Config File", config_path])
        start_time = datetime.now(tz=local_tz)
        csv_writer.writerow(
            ["Start Time", start_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z")]
        )
        csv_writer.writerow([])

        channel_names_with_units = [
            f"{name} ({unit})" for name, unit in zip(channel_names, units)
        ]
        csv_writer.writerow(
            [
                *channel_names_with_units,
                *(
                    f"Raw {name}"
                    for name, save_value in zip(channel_names, save_raw)
                    if save_value
                ),
            ]
        )

        # Flush RX buffer.
        ser.flush()

        while True:
            # Parse raw values.
            line = ser.readline()
            raw_readings = [int(float(reading)) for reading in line.decode().split()]
            raw_outputs = [
                reading for reading, save in zip(raw_readings, save_raw) if not save
            ]

            converted_readings = [
                scale * reading + offset
                for scale, reading, offset in zip(scales, raw_readings, offsets)
            ]

            csv_writer.writerow([*converted_readings, *raw_outputs])
            print(
                ", ".join(
                    "{:}: {:6.2f} {:}".format(name, value, unit)
                    for name, value, unit in zip(
                        channel_names, converted_readings, units
                    )
                )
            )


if __name__ == "__main__":
    available_ports = [port.name for port in serial.tools.list_ports.comports()]

    parser = argparse.ArgumentParser(
        prog="Coax Drone Force Measurement Interface",
        description="Reads data from load cells in the force measurement jig",
    )
    parser.add_argument(
        "--port", "-p", help=f"Serial port, found: {', '.join(available_ports)}"
    )
    parser.add_argument(
        "--out",
        default="experiments_479",
        type=Path,
        help="Path to experiment directory",
    )
    parser.add_argument(
        "--config",
        default="config.yml",
        type=str,
        help="Name of the file where configs are stored",
    )
    args = parser.parse_args()

    run_experiment(args.port, args.out, args.config)
