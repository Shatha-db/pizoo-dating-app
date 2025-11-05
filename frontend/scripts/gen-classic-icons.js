// Generate Classic Logo PNG icons from SVG
const fs = require("fs");
const path = require("path");
const sharp = require("sharp");

const ROOT = path.join(__dirname, "..");
const SRC  = path.join(ROOT, "public/logo/logo_classic.svg");
const OUT  = path.join(ROOT, "public/logo");

if (!fs.existsSync(OUT)) {
  fs.mkdirSync(OUT, { recursive: true });
}

(async () => {
  console.log('🎨 Generating Classic Pizoo icons...\n');
  
  try {
    const svgBuf = fs.readFileSync(SRC);
    
    // logo_classic_1024.png
    await sharp(svgBuf, { density: 300 })
      .resize(1024, 1024, { fit: 'contain', background: { r: 255, g: 255, b: 255, alpha: 0 } })
      .png({ compressionLevel: 9 })
      .toFile(path.join(OUT, "logo_classic_1024.png"));
    console.log('✓ logo_classic_1024.png');
    
    // logo_classic_512.png
    await sharp(svgBuf, { density: 300 })
      .resize(512, 512, { fit: 'contain', background: { r: 255, g: 255, b: 255, alpha: 0 } })
      .png({ compressionLevel: 9 })
      .toFile(path.join(OUT, "logo_classic_512.png"));
    console.log('✓ logo_classic_512.png');
    
    // favicon.png (64x64)
    await sharp(svgBuf, { density: 300 })
      .resize(64, 64, { fit: 'contain', background: { r: 255, g: 255, b: 255, alpha: 0 } })
      .png({ compressionLevel: 9 })
      .toFile(path.join(OUT, "favicon.png"));
    console.log('✓ favicon.png');
    
    // Also generate standard sizes for fallback
    await sharp(svgBuf, { density: 300 })
      .resize(192, 192, { fit: 'contain', background: { r: 255, g: 255, b: 255, alpha: 0 } })
      .png({ compressionLevel: 9 })
      .toFile(path.join(OUT, "logo192.png"));
    console.log('✓ logo192.png');
    
    console.log('\n✅ All Classic logos generated!');
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
})();
