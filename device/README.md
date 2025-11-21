# Device Software

Python application running on Raspberry Pi 5 for network scanning and report generation.

## Hardware Requirements

- Raspberry Pi 5 (8 GB RAM)
- PoE HAT
- e-Ink HAT Display (compatible with Waveshare or similar)
- Red push button (GPIO)

## Installation

```bash
# Create virtual environment
sudo mkdir -p /opt/yfitg-scout
sudo python3 -m venv /opt/yfitg-scout/.venv
source /opt/yfitg-scout/.venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install systemd service
sudo cp yfitg-scout.service /etc/systemd/system/
sudo systemctl enable yfitg-scout
sudo systemctl start yfitg-scout
```

## Configuration

Copy `config.example.json` to `.config.json` and fill in:

- `device_id`: Unique device identifier
- `mqtt_broker`: MQTT broker hostname
- `mqtt_port`: MQTT broker port (usually 8883 for TLS)
- `mqtt_username`: MQTT username
- `mqtt_password`: MQTT password
- `collector_api_url`: Report collector API endpoint
- `collector_api_token`: API authentication token
- `llm_model_path`: Path to GGUF model file

## Usage

The service starts automatically on boot. Manual control:

```bash
sudo systemctl start yfitg-scout
sudo systemctl stop yfitg-scout
sudo systemctl status yfitg-scout
```

## Logs

```bash
journalctl -u yfitg-scout -f
```

## Windows Development

For development and testing on Windows:

```powershell
# Navigate to device directory
cd device

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
New-Item -ItemType Directory -Force -Path logs, reports, templates, certs, models, assets\animations

# Copy and configure
Copy-Item config.example.json .config.json
# Edit .config.json with your settings

# Run the device software
python main.py
```

**Note:** The software automatically detects Windows and uses the current directory instead of `/opt/yfitg-scout/`. You can override this by setting the `YFITG_SCOUT_BASE_DIR` environment variable.

**Important:** Some features (GPIO button, e-Ink display) will not work on Windows and will use mock implementations.

