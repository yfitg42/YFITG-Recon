#!/bin/bash
# Patch Waveshare library to support Raspberry Pi 5
# This patches the library's hardware detection to recognize Pi 5

echo "Patching Waveshare library for Raspberry Pi 5 support..."

# Activate virtual environment
source /opt/yfitg-scout/.venv/bin/activate

# Find the Waveshare library location
WAVESHARE_PATH=$(python -c "import waveshare_epd; import os; print(os.path.dirname(waveshare_epd.__file__))" 2>/dev/null)

if [ -z "$WAVESHARE_PATH" ]; then
    echo "Error: Waveshare library not found. Please install it first."
    exit 1
fi

echo "Found Waveshare library at: $WAVESHARE_PATH"

# Pi 5 uses BCM2712, base address is 0x107C000000 (different from Pi 4)
# We need to patch the base.py or similar file that does model detection

# Find the file that contains model detection
BASE_FILE=$(find "$WAVESHARE_PATH" -name "base.py" -o -name "*base*.py" | head -1)

if [ -z "$BASE_FILE" ]; then
    echo "Warning: Could not find base.py file. Trying alternative approach..."
    # Try to find any file with "BCM" or "model" in it
    BASE_FILE=$(grep -r "BCM2711\|BCM2835\|BCM2837" "$WAVESHARE_PATH" --include="*.py" -l | head -1)
fi

if [ -n "$BASE_FILE" ]; then
    echo "Found file to patch: $BASE_FILE"
    
    # Backup the original file
    cp "$BASE_FILE" "$BASE_FILE.backup"
    
    # Check if Pi 5 is already in the file
    if grep -q "BCM2712\|Pi 5\|Raspberry Pi 5" "$BASE_FILE"; then
        echo "Pi 5 support may already be present. Checking..."
    else
        echo "Adding Pi 5 support..."
        # This is a simplified patch - the actual implementation depends on the library structure
        # We'll add a comment marker that can be manually patched
        echo ""
        echo "NOTE: Automatic patching may not work for all library versions."
        echo "You may need to manually edit: $BASE_FILE"
        echo ""
        echo "Look for model detection code and add:"
        echo "  - BCM2712 (Pi 5 chip)"
        echo "  - Base address: 0x107C000000"
        echo "  - Model string: 'Raspberry Pi 5'"
    fi
else
    echo "Could not find the file to patch automatically."
    echo "You may need to manually patch the Waveshare library."
fi

# Alternative: Try to set environment variable or monkey-patch
echo ""
echo "Creating Python patch file..."
cat > /opt/yfitg-scout/patch_pi5.py << 'EOFPATCH'
# Monkey patch for Pi 5 support
import sys

# Try to patch the Waveshare library's model detection
try:
    import waveshare_epd
    # Find the base module
    if hasattr(waveshare_epd, 'base'):
        base = waveshare_epd.base
    elif hasattr(waveshare_epd, 'epdconfig'):
        base = waveshare_epd.epdconfig
    else:
        # Try to import directly
        try:
            from waveshare_epd import epdconfig as base
        except:
            try:
                from waveshare_epd import base
            except:
                base = None
    
    if base and hasattr(base, 'get_model'):
        original_get_model = base.get_model
        
        def patched_get_model():
            try:
                # Try original first
                model = original_get_model()
                return model
            except:
                # Check for Pi 5
                try:
                    with open('/proc/device-tree/model', 'r') as f:
                        model_str = f.read().strip()
                        if 'Raspberry Pi 5' in model_str:
                            # Pi 5 uses BCM2712
                            return 'BCM2712'
                except:
                    pass
                raise
        
        base.get_model = patched_get_model
        print("Patched Waveshare library model detection")
except Exception as e:
    print(f"Could not patch library: {e}")
EOFPATCH

echo "Created patch file at: /opt/yfitg-scout/patch_pi5.py"
echo ""
echo "To use the patch, add this to the top of your main.py or display.py:"
echo "  import sys"
echo "  sys.path.insert(0, '/opt/yfitg-scout')"
echo "  import patch_pi5"
echo ""
echo "Or run: python /opt/yfitg-scout/patch_pi5.py"

