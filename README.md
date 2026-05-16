# Airthings Wave Plus Sensor Reader

Read current sensor values from [Airthings Wave Plus](https://airthings.com/wave-plus/) devices over Bluetooth Low Energy (BLE).

Sensors: humidity, temperature, radon (short/long term), atmospheric pressure, CO2, and TVOC.

## Requirements

- Python 3.9+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- A Bluetooth adapter (built-in on Raspberry Pi 3/4/5)
- Linux, macOS, or Windows (via `bleak`)

## Setup

```
git clone https://github.com/Airthings/waveplus-reader.git
cd waveplus-reader
uv sync
```

## Usage

Find the 10-digit serial number under the magnetic backplate of your Wave Plus.

If your device is paired to a phone, turn off Bluetooth on the phone first.

### Print to terminal

```
uv run python -u read_waveplus.py SN SAMPLE-PERIOD
```

### Pipe to file

```
uv run python -u read_waveplus.py SN SAMPLE-PERIOD pipe > output.txt
```

| Argument | Example | Description |
|----------|---------|-------------|
| SN | 2930066257 | 10-digit serial number |
| SAMPLE-PERIOD | 60 | Seconds between readings (must be > 0) |
| pipe | pipe > output.txt | Optional, output as plain lists instead of table |

> **Note:** Sensor values (except radon) update every 5 minutes. Radon updates hourly.

Exit with `Ctrl+C`.

## Sensor data

| Sensor | Units |
|--------|-------|
| Humidity | %rH |
| Temperature | °C |
| Radon short term average | Bq/m³ |
| Radon long term average | Bq/m³ |
| Relative atmospheric pressure | hPa |
| CO2 level | ppm |
| TVOC level | ppb |

## Dependencies

Managed via `pyproject.toml`:

- [bleak](https://github.com/hbldh/bleak) — cross-platform BLE
- [tableprint](https://github.com/nirum/tableprint) — terminal table formatting

## License

MIT
