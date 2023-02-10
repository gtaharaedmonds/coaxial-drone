import asyncio
from typing import List
import serial_asyncio
import csv
from pathlib import Path
from datetime import datetime
import argparse
from contextlib import asynccontextmanager


@asynccontextmanager
async def connect_to_device(port: str, timeout=10):
    """
    Asynchronous context manager to handle connecting to a test jig, querying its device id, timeout, and disconnecting on cleanup
    
    Returns (reader, writer, device_id)
    """
    async with asyncio.timeout(timeout) as timeout_manager:
        serial_reader, serial_writer = await serial_asyncio.open_serial_connection(port=port)
    try:
        async with timeout_manager:
            serial_writer.write(b'deviceid\n')
            await serial_writer.drain()
            device_id_bytes = await serial_reader.readline()
            try:
                device_id = int(device_id_bytes)
            except ValueError:
                raise ConnectionError(f'Received invalid device id data {device_id_bytes}')
        yield serial_reader, serial_writer, device_id
    finally:
        serial_writer.close()
        await serial_writer.wait_closed()


def load_settings(device_id: int, calibration_dir: Path):
    """
    Loads most recent calibration file for a given device id
    
    Returns (channel_names, offsets, scales)
    """

    calibration_path = max(
        file for file in calibration_dir.iterdir()
        if file.name.startswith(str(device_id)))

    with calibration_path.open() as calibration_file:
        csv_rows = csv.reader(calibration_file)
        # Skip capture time row
        next(csv_rows)
        # Skip column header row
        next(csv_rows)
        # For each of the next rows, ignore the first column and convert datatypes if required
        channel_names = next(csv_rows)[1:]
        offsets = [float(offset) for offset in next(csv_rows)[1:]]
        scales = [float(scale) for scale in next(csv_rows)[1:]]
        return channel_names, offsets, scales, calibration_path


async def run_experiment(port: str, experiment_dir: Path, calibration_dir: Path):
    """Main program flow"""
    async with connect_to_device(port) as (serial_reader, serial_writer, device_id):
        channel_names, scales, offsets, calibration_path = load_settings(device_id, calibration_dir)

        local_tz = datetime.now().astimezone().tzinfo
        file_time = datetime.now(tz=local_tz)
        with open(experiment_dir / f'{file_time:%Y-%m-%dT%H:%M:%S%z}.csv', 'w') as csv_file:
            csv_writer = csv.writer(csv_file)

            # Write file header
            csv_writer.writerow(['device_id', device_id])
            csv_writer.writerow(['calibration_file', calibration_path])
            start_time = datetime.now(tz=local_tz)
            csv_writer.writerow(['start_time', start_time.strftime('%Y-%m-%dT%H:%M:%S.%f%z')])
            csv_writer.writerow([])
            csv_writer.writerow([*channel_names, *(f'ch{i}_raw' for i in range(len(channel_names)))])

            # Request the jig to start sending data
            serial_writer.write(b'start\n')
            await serial_writer.drain()

            async for line in serial_reader:
                raw_readings = [int(reading) for reading in line.decode().split()]
                calibrated_readings = [
                    scale * reading + offset
                    for scale, reading, offset
                    in zip(scales, raw_readings, offsets)]
                
                csv_writer.writerow([*calibrated_readings, *raw_readings])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Coax Drone Force Measurement Interface',
        description='Reads data from load cells in the force measurement jig')
    parser.add_argument('port', metavar='P', help='Serial port')
    parser.add_argument('--experiment-dir', default='experiments', type=Path, help='Path to experiment directory')
    parser.add_argument('--calibration-dir', default='calibration', type=Path, help='Path to device calibration/settings directory')
    args = parser.parse_args()

    asyncio.run(run_experiment(args.port, args.experiment_dir, args.calibration_dir))
