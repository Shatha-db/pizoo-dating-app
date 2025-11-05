// Generate PNG icons from SVG (requires `sharp`)
const fs = require("fs");
const path = require("path");
const sharp = require("sharp");

const ROOT = path.join(__dirname, "..");
const SRC  = path.join(ROOT, "src/assets/logo/pizoo.svg");
const PUB  = path.join(ROOT, "public");
const ICON = path.join(PUB, "icons");

if (!fs.existsSync(ICON)) {
  fs.mkdirSync(ICON, { recursive: true });
}

const sizes = [1024, 512, 384, 256, 192, 180, 167, 152, 144, 128, 96, 72, 64, 48, 32, 16];

(async () => {
  console.log('🎨 Generating Pizoo icons from SVG...\n');
  
  try {
    // Generate all standard sizes
    for (const s of sizes) {
      const out = path.join(ICON, `icon-${s}.png`);
      await sharp(SRC)
        .resize(s, s, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
        .png({ compressionLevel: 9 })
        .toFile(out);
      console.log(`✓ ${path.basename(out)}`);
    }
    
    console.log('\n📱 Generating PWA icons...\n');
    
    // Maskable icon (512x512)
    await sharp(SRC)
      .resize(512, 512, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
      .png({ compressionLevel: 9 })
      .toFile(path.join(ICON, "maskable-512.png"));
    console.log('✓ maskable-512.png');
    
    // Apple touch icon (180x180)
    await sharp(SRC)
      .resize(180, 180, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
      .png({ compressionLevel: 9 })
      .toFile(path.join(PUB, "apple-touch-icon.png"));
    console.log('✓ apple-touch-icon.png');
    
    console.log('\n🌐 Generating favicons...\n');
    
    // Favicon 32x32
    await sharp(SRC)
      .resize(32, 32, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
      .png()
      .toFile(path.join(PUB, "favicon-32.png"));
    console.log('✓ favicon-32.png');
    
    // Favicon 16x16
    await sharp(SRC)
      .resize(16, 16, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
      .png()
      .toFile(path.join(PUB, "favicon-16.png"));
    console.log('✓ favicon-16.png');
    
    console.log('\n✅ All icons generated successfully!');
    console.log(`📊 Total icons: ${sizes.length + 4}`);
    console.log(`📁 Output: ${ICON}`);
  } catch (error) {
    console.error('❌ Error generating icons:', error.message);
    process.exit(1);
  }
})();
