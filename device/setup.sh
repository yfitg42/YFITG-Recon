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

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install system dependencies (if needed)
echo "Installing system dependencies..."
apt-get update
apt-get install -y nmap nikto python3-dev libssl-dev

# Copy configuration template
if [ ! -f /opt/yfitg-scout/.config.json ]; then
    echo "Copying configuration template..."
    cp config.example.json /opt/yfitg-scout/.config.json
    echo "Please edit /opt/yfitg-scout/.config.json with your settings"
fi

# Install systemd service
echo "Installing systemd service..."
cp yfitg-scout.service /etc/systemd/system/
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

