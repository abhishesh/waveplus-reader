# MIT License
#
# Copyright (c) 2018 Airthings AS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# https://airthings.com

import asyncio
import struct
import sys
import time

import tableprint
from bleak import BleakClient, BleakScanner

# ===============================
# Script guards for correct usage
# ===============================

USAGE = (
    "USAGE: read_waveplus.py SN SAMPLE-PERIOD [pipe > yourfile.txt]\n"
    "    SN: 10-digit serial number found under the magnetic backplate.\n"
    "    SAMPLE-PERIOD: time in seconds between readings (must be > 0).\n"
    "    pipe: optional, pipe output to a file."
)

if len(sys.argv) < 3:
    sys.exit(f"ERROR: Missing input argument SN or SAMPLE-PERIOD.\n{USAGE}")

if not sys.argv[1].isdigit() or len(sys.argv[1]) != 10:
    sys.exit(f"ERROR: Invalid SN format.\n{USAGE}")

if not sys.argv[2].isdigit() or int(sys.argv[2]) <= 0:
    sys.exit(f"ERROR: Invalid SAMPLE-PERIOD. Must be larger than zero.\n{USAGE}")

Mode = sys.argv[3].lower() if len(sys.argv) > 3 else "terminal"
if Mode not in ("pipe", "terminal"):
    sys.exit(f"ERROR: Invalid piping method.\n{USAGE}")

SerialNumber = int(sys.argv[1])
SamplePeriod = int(sys.argv[2])

# ===============================
# Constants
# ===============================

CHARACTERISTIC_UUID = "b42e2a68-ade7-11e4-89d3-123b93f75cba"
AIRTHINGS_MANUFACTURER_ID = 0x0334

SENSOR_NAMES = ["Humidity", "Radon ST avg", "Radon LT avg", "Temperature", "Pressure", "CO2 level", "VOC level"]
SENSOR_UNITS = ["%rH", "Bq/m3", "Bq/m3", "degC", "hPa", "ppm", "ppb"]

# ===============================
# Utility functions
# ===============================


def parse_serial_number(manufacturer_data: dict) -> int | None:
    """Extract serial number from BLE manufacturer data."""
    data = manufacturer_data.get(AIRTHINGS_MANUFACTURER_ID)
    if data is None:
        return None
    if len(data) >= 4:
        return struct.unpack_from("<I", data, 0)[0]
    return None


def parse_sensor_data(raw: bytes) -> list[str] | None:
    """Parse raw characteristic data into formatted sensor strings."""
    values = struct.unpack("<BBBBHHHHHHHH", raw)
    version = values[0]
    if version != 1:
        print("ERROR: Unknown sensor version. Contact Airthings for support.")
        return None

    humidity = values[1] / 2.0
    radon_st = values[4] if 0 <= values[4] <= 16383 else "N/A"
    radon_lt = values[5] if 0 <= values[5] <= 16383 else "N/A"
    temperature = values[6] / 100.0
    pressure = values[7] / 50.0
    co2 = values[8] * 1.0
    voc = values[9] * 1.0

    sensor_values = [humidity, radon_st, radon_lt, temperature, pressure, co2, voc]
    return [f"{v} {u}" for v, u in zip(sensor_values, SENSOR_UNITS)]


# ===============================
# Main
# ===============================


async def find_device():
    """Scan for the Wave Plus with the matching serial number."""
    print(f"Scanning for device with serial number {SerialNumber}...")
    for _ in range(50):
        devices = await BleakScanner.discover(timeout=2.0, return_adv=True)
        for _, (dev, adv) in devices.items():
            sn = parse_serial_number(adv.manufacturer_data)
            if sn == SerialNumber:
                return dev
    return None


async def main():
    device = await find_device()
    if device is None:
        sys.exit(
            "ERROR: Could not find device.\n"
            "GUIDE: (1) Verify the serial number.\n"
            "       (2) Ensure the device is advertising.\n"
            "       (3) Retry connection."
        )

    if Mode == "terminal":
        print("\nPress ctrl+C to exit program\n")
    print(f"Device serial number: {SerialNumber}")

    if Mode == "terminal":
        print(tableprint.header(SENSOR_NAMES, width=12))
    else:
        print(SENSOR_NAMES)

    while True:
        try:
            async with BleakClient(device) as client:
                raw = await client.read_gatt_char(CHARACTERISTIC_UUID)
                data = parse_sensor_data(raw)
                if data is None:
                    sys.exit(1)
                if Mode == "terminal":
                    print(tableprint.row(data, width=12))
                else:
                    print(data)
        except Exception as e:
            print(f"WARNING: Connection error: {e}. Retrying...")

        await asyncio.sleep(SamplePeriod)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting.")
