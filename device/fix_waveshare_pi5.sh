#!/bin/bash
# Fix Waveshare library for Raspberry Pi 5
# Pi 5 support is better in the GitHub version

echo "Fixing Waveshare library for Raspberry Pi 5..."

# Activate virtual environment
source /opt/yfitg-scout/.venv/bin/activate

# Uninstall current version
echo "Uninstalling current waveshare-epd..."
pip uninstall -y waveshare-epd 2>/dev/null || true

# Install from GitHub (has better Pi 5 support)
echo "Installing Waveshare library from GitHub..."
cd /tmp
if [ -d "e-Paper" ]; then
    rm -rf e-Paper
fi

git clone https://github.com/waveshare/e-Paper.git
cd e-Paper/RaspberryPi_JetsonNano/python

# Install using the venv's python
echo "Installing library..."
/opt/yfitg-scout/.venv/bin/python setup.py install

# Verify installation
echo ""
echo "Verifying installation..."
python -c "from waveshare_epd import epd7in5_V2; print('✓ Waveshare library imported successfully')" && {
    echo "✓ Installation successful!"
} || {
    echo "✗ Installation failed"
    exit 1
}

echo ""
echo "Done! The library should now work with Raspberry Pi 5."
echo "Try running: python main.py"

