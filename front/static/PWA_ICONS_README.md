# PWA Icon Generation Guide

## Required Icons

You need to create the following icon files in this `/static/` folder:

1. **pwa-192x192.png** - 192×192px (standard icon)
2. **pwa-512x512.png** - 512×512px (standard icon)
3. **pwa-192x192-maskable.png** - 192×192px (adaptive icon with safe zone)
4. **pwa-512x512-maskable.png** - 512×512px (adaptive icon with safe zone)
5. **apple-touch-icon.png** - 180×180px (iOS home screen)
6. **favicon.ico** - 32×32px (browser tab)

## Quick Generation Methods

### Option 1: PWA Builder (Recommended)
1. Visit https://www.pwabuilder.com/imageGenerator
2. Upload a 512×512px source image (bus icon with brand colors)
3. Download the generated icon package
4. Extract and copy to `/static/` folder

### Option 2: Manual Design
Design your icon in Figma/Photoshop/GIMP:
- Use bus-themed design
- Colors: #3b82f6 (brand blue), #ffffff (white)
- Export at required sizes above

### Option 3: Use Maskable.app
1. Visit https://maskable.app/editor
2. Upload your design
3. Adjust safe zone (inner 80% circle)
4. Export maskable variants

## Icon Design Guidelines

### Standard Icons (any purpose)
- Can use full canvas
- Include padding if desired
- Clear, recognizable at small sizes

### Maskable Icons (adaptive)
- **Critical**: Keep important content in inner 80% circle (safe zone)
- Outer 20% may be cropped on some devices
- Use solid background color
- Test with Maskable.app

### Current Placeholders
Placeholder PNG files have been created for development.
**Replace these with actual branded icons before production deployment!**

## Testing Your Icons

1. Open Chrome DevTools → Application → Manifest
2. Check that all icons load correctly
3. Verify sizes and purposes match
4. Test install on Android device
5. Check home screen icon appearance
