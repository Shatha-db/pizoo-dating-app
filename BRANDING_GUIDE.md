# 🎨 PiZOO Branding Guide

## Logo Files

### Primary Logos (SVG)

**Brand Version (Red/Orange Gradient):**
- Location: `/frontend/public/brand/pizoo-logo.svg`
- Colors: #FF7A45 → #FF3B2E
- Usage: Main logo for app header, landing page, general use

**Gold Version (Premium):**
- Location: `/frontend/public/brand/pizoo-logo-gold.svg`
- Colors: #FFD479 → #FFC245 → #FF9C00
- Usage: Premium features, splash screens, special events

### Logo Specifications

**Dimensions:**
- Original: 1400×560px
- Aspect Ratio: 2.5:1
- Text: "PiZOO" (capital P)
- Font: Luckiest Guy

**Features:**
- Transparent background
- Gradient fills
- Soft glow effects
- Halftone pattern (brand version)
- Stroke outlines for depth

---

## React Component Usage

### Installation

The Logo component is located at:
```
/frontend/src/components/Logo.tsx
```

### Basic Usage

```tsx
import Logo from '@/components/Logo';

// Default (brand version, 220px width)
<Logo />

// Custom size
<Logo width={180} />

// Gold variant
<Logo variant="gold" width={280} />

// With custom className
<Logo width={200} className="my-logo" />
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | 'brand' \| 'gold' | 'brand' | Logo color scheme |
| width | number \| string | 220 | Logo width in pixels or CSS unit |
| height | number \| string | 'auto' | Logo height (auto maintains ratio) |
| className | string | undefined | Additional CSS classes |
| title | string | 'PiZOO' | Accessibility label |

---

## PNG Assets (To Be Generated)

### Web Assets

**Header/General Use:**
```
/frontend/public/brand/png/
├── 512x200.png          # Large header
├── 256x100.png          # Small header
├── 512x200-gold.png     # Gold large
└── 256x100-gold.png     # Gold small
```

### PWA Icons

**App Icons (Transparent):**
```
/frontend/public/icons/
├── icon-512x512.png     # Large app icon
├── icon-384x384.png     # Medium app icon
├── icon-192x192.png     # Standard app icon
├── icon-128x128.png     # Small app icon
└── icon-64x64.png       # Tiny app icon
```

**Favicons:**
```
/frontend/public/
├── favicon-48.png
├── favicon-32.png
├── favicon-16.png
└── favicon.ico          # Combined ICO file
```

---

## Generation Instructions

### Method 1: Using Inkscape (Recommended)

```bash
# Install Inkscape
sudo apt-get install inkscape

# Convert SVG to PNG (512x200)
inkscape pizoo-logo.svg \
  --export-filename=512x200.png \
  --export-width=512 \
  --export-height=200 \
  --export-background-opacity=0

# For square icons (centered)
inkscape pizoo-logo.svg \
  --export-filename=icon-512x512.png \
  --export-width=512 \
  --export-height=512 \
  --export-background-opacity=0 \
  --export-area-page
```

### Method 2: Using Sharp (Node.js)

```bash
# Install Sharp
cd /app/frontend
yarn add -D sharp

# Create conversion script
node scripts/generate-icons.js
```

**Script Example:**

```javascript
const sharp = require('sharp');
const fs = require('fs');

const sizes = [
  { w: 512, h: 200, name: '512x200' },
  { w: 256, h: 100, name: '256x100' },
  { w: 512, h: 512, name: 'icon-512x512' },
  { w: 384, h: 384, name: 'icon-384x384' },
  { w: 192, h: 192, name: 'icon-192x192' },
  { w: 128, h: 128, name: 'icon-128x128' },
  { w: 64, h: 64, name: 'icon-64x64' },
  { w: 48, h: 48, name: 'favicon-48' },
  { w: 32, h: 32, name: 'favicon-32' },
  { w: 16, h: 16, name: 'favicon-16' },
];

const inputSvg = 'public/brand/pizoo-logo.svg';

sizes.forEach(({ w, h, name }) => {
  const output = name.includes('icon-') 
    ? `public/icons/${name}.png`
    : name.includes('favicon')
    ? `public/${name}.png`
    : `public/brand/png/${name}.png`;

  sharp(inputSvg)
    .resize(w, h, {
      fit: 'contain',
      background: { r: 0, g: 0, b: 0, alpha: 0 }
    })
    .png()
    .toFile(output)
    .then(() => console.log(`✅ Generated ${output}`))
    .catch(err => console.error(`❌ Error ${name}:`, err));
});
```

### Method 3: Using GIMP

1. Open SVG in GIMP
2. Set desired size
3. Export as PNG with transparency
4. Repeat for all sizes

---

## Outline Fonts (Production SVG)

### Why Outline Fonts?

- No dependency on Google Fonts
- Consistent rendering across all browsers
- Faster loading (no external font download)
- Works offline

### How to Outline

**Using Inkscape:**

```bash
# Convert text to paths
inkscape pizoo-logo.svg \
  --actions="select-all;object-to-path;export-filename:pizoo-logo-outlined.svg;export-do" \
  --batch-process
```

**Manual Steps:**

1. Open SVG in Inkscape
2. Select text object
3. Path → Object to Path (Ctrl+Shift+C)
4. Save as new file
5. Replace original with outlined version

---

## Manifest.json Update

Update `/frontend/public/manifest.json`:

```json
{
  "name": "PiZOO Dating App",
  "short_name": "PiZOO",
  "description": "Connect and date with PiZOO",
  "icons": [
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-384x384.png",
      "sizes": "384x384",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-128x128.png",
      "sizes": "128x128",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-64x64.png",
      "sizes": "64x64",
      "type": "image/png"
    }
  ],
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#FF4458",
  "background_color": "#FFFFFF"
}
```

---

## Color Palette

### Brand Colors

**Primary Gradient:**
```css
--brand-orange-start: #FF7A45;
--brand-red-end: #FF3B2E;
--brand-gradient: linear-gradient(135deg, #FF7A45 0%, #FF3B2E 100%);
```

**Gold Gradient:**
```css
--gold-light: #FFD479;
--gold-mid: #FFC245;
--gold-dark: #FF9C00;
--gold-gradient: linear-gradient(135deg, #FFD479 0%, #FFC245 45%, #FF9C00 100%);
```

**Accent Colors:**
```css
--brand-stroke: #9B1C13;     /* Dark red for text stroke */
--gold-stroke: #B86D00;      /* Dark gold for text stroke */
--primary: #FF4458;          /* Main theme color */
--secondary: #10b981;        /* Success/secondary color */
```

---

## Usage Guidelines

### Do's ✅

- Use brand version for general app UI
- Use gold version for premium features
- Maintain aspect ratio (2.5:1)
- Use on light or dark backgrounds
- Keep minimum width of 120px for readability
- Use Logo component for React apps

### Don'ts ❌

- Don't stretch or distort the logo
- Don't change colors or gradients
- Don't add drop shadows (glow is built-in)
- Don't place on busy backgrounds
- Don't use low-quality raster versions when SVG is available
- Don't modify the "PiZOO" text or spacing

---

## Implementation Checklist

- [x] Create brand SVG logo
- [x] Create gold SVG logo
- [x] Create React Logo component
- [ ] Generate PNG assets (512x200, 256x100)
- [ ] Generate PWA icons (512, 384, 192, 128, 64)
- [ ] Generate favicons (48, 32, 16, ico)
- [ ] Outline fonts in SVGs
- [ ] Update manifest.json
- [ ] Update header/navbar to use new logo
- [ ] Update landing page
- [ ] Update splash screen
- [ ] Test on light/dark backgrounds
- [ ] Verify PWA icons in browser
- [ ] Test favicon in browser tabs

---

## Support

For questions or issues with branding assets:
- Check this guide first
- Review `/app/frontend/src/components/Logo.tsx`
- Verify SVG files in `/app/frontend/public/brand/`

---

**Last Updated:** 2025-01-02  
**Version:** 1.0.0  
**Status:** SVG files created, PNG generation pending
