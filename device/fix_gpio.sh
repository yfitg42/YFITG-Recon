#!/bin/bash
# Fix GPIO installation for Raspberry Pi
# This script removes Jetson.GPIO and installs the correct RPi.GPIO

echo "Fixing GPIO installation for Raspberry Pi..."

# Activate virtual environment
source /opt/yfitg-scout/.venv/bin/activate

# Uninstall Jetson.GPIO and any incorrect RPi.GPIO
echo "Uninstalling Jetson.GPIO..."
pip uninstall -y Jetson.GPIO 2>/dev/null || true

# Uninstall current RPi.GPIO (might be Jetson compatibility layer)
echo "Uninstalling current RPi.GPIO..."
pip uninstall -y RPi.GPIO 2>/dev/null || true

# Install system package for RPi.GPIO (this is the correct one for Raspberry Pi)
echo "Installing system RPi.GPIO package..."
sudo apt-get update
sudo apt-get install -y python3-rpi.gpio

# Install RPi.GPIO in virtual environment
echo "Installing RPi.GPIO in virtual environment..."
pip install --no-deps RPi.GPIO || {
    echo "Trying alternative installation method..."
    # If direct install fails, create symlink to system package
    SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")
    if [ -d "/usr/lib/python3/dist-packages/RPi" ]; then
        echo "Creating symlink to system RPi.GPIO..."
        ln -sf /usr/lib/python3/dist-packages/RPi "$SITE_PACKAGES/" 2>/dev/null || true
    fi
}

# Verify installation
echo ""
echo "Verifying GPIO installation..."
python -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); print('✓ RPi.GPIO working correctly')" && {
    echo "✓ GPIO fixed successfully!"
} || {
    echo "✗ GPIO still has issues. Try rebooting and ensure SPI is enabled."
}

echo ""
echo "Done! Try running python main.py again."

