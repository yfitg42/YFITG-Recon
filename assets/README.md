# Assets Directory

This directory contains static assets for the YFITG Network Scout system.

## Structure

```
assets/
├── animations/     # e-Ink display animation frames
├── logos/          # YFITG branding assets
└── models/         # 3D printer STL files for enclosure
```

## Animation Frames

Place animation frames in `animations/` directory:
- `frame_00.png` through `frame_05.png` (or more)
- Recommended: 800x480 pixels, 1-bit (black/white) for e-Ink
- Format: PNG

The device will automatically load these frames if present, otherwise it will generate simple placeholder animations.

## Logos

Place YFITG logo files in `logos/`:
- `logo.png` - Main logo (for PDF reports)
- `logo_small.png` - Small logo variant
- `favicon.ico` - Website favicon

## 3D Models

Place STL files for 3D-printed enclosure in `models/`:
- `enclosure_top.stl`
- `enclosure_bottom.stl`
- `label_template.stl` (for label printing)

## Usage

Copy assets to device:
```bash
sudo cp -r assets/* /opt/yfitg-scout/assets/
```

