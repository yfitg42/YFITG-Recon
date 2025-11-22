#!/bin/bash
# YFITG Network Scout - Device Setup Script

set -e

echo "YFITG Network Scout - Device Setup"
echo "=================================="

# Check if running as root for system operations
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Create directories
echo "Creating directories..."
mkdir -p /opt/yfitg-scout/{logs,reports,models,templates,certs}
mkdir -p /opt/yfitg-scout/assets/animations

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv /opt/yfitg-scout/.venv
source /opt/yfitg-scout/.venv/bin/activate

# Install system dependencies (if needed)
echo "Installing system dependencies..."
apt-get update
apt-get install -y nmap nikto python3-dev libssl-dev git python3-spidev

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip

# Remove any Jetson.GPIO or incorrect RPi.GPIO packages first
echo "Cleaning up GPIO packages..."
pip uninstall -y Jetson.GPIO RPi.GPIO 2>/dev/null || true

# Install correct RPi.GPIO for Raspberry Pi (not Jetson compatibility layer)
echo "Installing RPi.GPIO for Raspberry Pi..."
pip install --no-deps RPi.GPIO || {
    # If pip install fails, try system package
    apt-get install -y python3-rpi.gpio
    # Link system package to venv if needed
    if [ -f /usr/lib/python3/dist-packages/RPi/GPIO/__init__.py ]; then
        ln -sf /usr/lib/python3/dist-packages/RPi /opt/yfitg-scout/.venv/lib/python3.*/site-packages/ 2>/dev/null || true
    fi
}

pip install -r requirements.txt

# Install Waveshare e-Paper library (optional, for e-Ink display)
echo "Installing Waveshare e-Paper library (optional)..."
if pip install waveshare-epd 2>/dev/null; then
    echo "Successfully installed waveshare-epd"
else
    echo "Warning: Could not install waveshare-epd via pip. Trying alternative method..."
    # Install setuptools if not already installed (needed for setup.py)
    pip install setuptools wheel 2>/dev/null || true
    # Try installing from GitHub as fallback
    SAVE_DIR=$(pwd)
    cd /tmp
    if [ -d "e-Paper" ]; then
        rm -rf e-Paper
    fi
    if git clone https://github.com/waveshare/e-Paper.git 2>/dev/null; then
        cd e-Paper/RaspberryPi_JetsonNano/python
        # Make sure we're using the venv's python
        if /opt/yfitg-scout/.venv/bin/python setup.py install 2>/dev/null; then
            echo "Successfully installed Waveshare library from GitHub"
        else
            echo "Warning: Could not install Waveshare library from GitHub. Display will use mock mode."
        fi
    else
        echo "Warning: Could not clone Waveshare repository. Display will use mock mode."
    fi
    cd "$SAVE_DIR"
fi

# Copy Python source files
echo "Copying Python source files..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Script directory: $SCRIPT_DIR"

# Verify we're in the right place
if [ ! -f "$SCRIPT_DIR/main.py" ]; then
    echo "Error: main.py not found in $SCRIPT_DIR"
    echo "Please run this script from the device directory"
    exit 1
fi

# Copy all Python files
echo "Copying Python files from $SCRIPT_DIR to /opt/yfitg-scout/..."
for pyfile in "$SCRIPT_DIR"/*.py; do
    if [ -f "$pyfile" ]; then
        filename=$(basename "$pyfile")
        echo "  Copying $filename..."
        cp "$pyfile" /opt/yfitg-scout/
    fi
done

# Verify main.py was copied
if [ ! -f /opt/yfitg-scout/main.py ]; then
    echo "Error: main.py was not copied successfully"
    echo "Source directory: $SCRIPT_DIR"
    echo "Files in source:"
    ls -la "$SCRIPT_DIR"/*.py || echo "No .py files found"
    echo "Destination directory: /opt/yfitg-scout/"
    ls -la /opt/yfitg-scout/ || echo "Directory does not exist"
    exit 1
fi
echo "Successfully copied Python files"

# Copy templates directory
if [ -d "$SCRIPT_DIR/templates" ]; then
    echo "Copying templates..."
    cp -r "$SCRIPT_DIR/templates" /opt/yfitg-scout/
fi

# Copy configuration template
if [ ! -f /opt/yfitg-scout/.config.json ]; then
    echo "Copying configuration template..."
    cp "$SCRIPT_DIR/config.example.json" /opt/yfitg-scout/.config.json
    echo "Please edit /opt/yfitg-scout/.config.json with your settings"
fi

# Install systemd service
echo "Installing systemd service..."
cp "$SCRIPT_DIR/yfitg-scout.service" /etc/systemd/system/
systemctl daemon-reload

# Set permissions
echo "Setting permissions..."
# Detect the user who ran sudo, or fall back to current user
SCOUT_USER="${SUDO_USER:-$USER}"
if [ -z "$SCOUT_USER" ] || [ "$SCOUT_USER" = "root" ]; then
    # If we can't determine the user, try common defaults
    if id "pi" &>/dev/null; then
        SCOUT_USER="pi"
    else
        # Get the first non-root user
        SCOUT_USER=$(getent passwd | awk -F: '$3 >= 1000 && $1 != "nobody" {print $1; exit}')
        if [ -z "$SCOUT_USER" ]; then
            echo "Warning: Could not determine user. Using 'root' (not recommended)."
            SCOUT_USER="root"
        fi
    fi
fi
echo "Using user: $SCOUT_USER"
chown -R "$SCOUT_USER:$SCOUT_USER" /opt/yfitg-scout
chmod +x /opt/yfitg-scout/main.py

# Update systemd service file with the correct user
echo "Updating systemd service with user: $SCOUT_USER"
sed -i "s/^User=.*/User=$SCOUT_USER/" /etc/systemd/system/yfitg-scout.service
systemctl daemon-reload

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit /opt/yfitg-scout/.config.json with your configuration"
echo "2. Download LLM model to /opt/yfitg-scout/models/ (optional)"
echo "3. Add animation frames to /opt/yfitg-scout/assets/animations/ (optional)"
echo "4. Enable and start the service:"
echo "   sudo systemctl enable yfitg-scout"
echo "   sudo systemctl start yfitg-scout"
echo "5. Check status: sudo systemctl status yfitg-scout"
echo "6. View logs: journalctl -u yfitg-scout -f"

