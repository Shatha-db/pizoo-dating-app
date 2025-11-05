import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import sharp from 'sharp';
import toIco from 'to-ico';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const root = path.resolve(__dirname, '../src/assets/branding');
const svgWordmark = path.join(root, 'logo-wordmark.svg');
const svgMark = path.join(root, 'logo-mark.svg');
const outDir = path.join(root, 'png');

if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

const sizes = [16, 32, 48, 64, 96, 128, 192, 256, 384, 512, 1024];

async function makePngs(svgPath, baseName = 'logo') {
  if (!fs.existsSync(svgPath)) {
    console.warn(`⚠️  ${svgPath} not found, skipping...`);
    return;
  }

  const svgBuf = fs.readFileSync(svgPath);
  await Promise.all(
    sizes.map(async (sz) => {
      const out = path.join(outDir, `${baseName}-${sz}.png`);
      await sharp(svgBuf, { density: 300 })
        .resize(sz, sz, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
        .png()
        .toFile(out);
      console.log(`✓ Generated ${baseName}-${sz}.png`);
    })
  );
}

// أيقونات PWA الشائعة
async function makePwaIcons(svgPath) {
  if (!fs.existsSync(svgPath)) {
    console.warn(`⚠️  ${svgPath} not found, skipping PWA icons...`);
    return;
  }

  const svgBuf = fs.readFileSync(svgPath);

  // Android Chrome 192x192
  await sharp(svgBuf, { density: 300 })
    .resize(192, 192, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
    .png()
    .toFile(path.join(outDir, 'android-chrome-192x192.png'));
  console.log('✓ Generated android-chrome-192x192.png');

  // Android Chrome 512x512
  await sharp(svgBuf, { density: 300 })
    .resize(512, 512, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
    .png()
    .toFile(path.join(outDir, 'android-chrome-512x512.png'));
  console.log('✓ Generated android-chrome-512x512.png');

  // Apple Touch Icon 180x180
  await sharp(svgBuf, { density: 300 })
    .resize(180, 180, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
    .png()
    .toFile(path.join(outDir, 'apple-touch-icon.png'));
  console.log('✓ Generated apple-touch-icon.png');
}

// favicon.ico (16, 32, 48)
async function makeFavicon(svgPath) {
  if (!fs.existsSync(svgPath)) {
    console.warn(`⚠️  ${svgPath} not found, skipping favicon...`);
    return;
  }

  const svgBuf = fs.readFileSync(svgPath);
  const icoPngs = await Promise.all(
    [16, 32, 48].map((sz) =>
      sharp(svgBuf, { density: 300 })
        .resize(sz, sz, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
        .png()
        .toBuffer()
    )
  );
  const ico = await toIco(icoPngs);
  const publicDir = path.resolve(__dirname, '../public');
  fs.writeFileSync(path.join(publicDir, 'favicon.ico'), ico);
  console.log('✓ Generated favicon.ico');
}

(async () => {
  console.log('🎨 Starting icon generation...\n');

  // Use logo-mark for square icons (PWA, favicon)
  const squareSvg = fs.existsSync(svgMark) ? svgMark : svgWordmark;

  // Generate all PNG sizes from wordmark
  await makePngs(svgWordmark, 'wordmark');

  // Generate all PNG sizes from mark
  if (fs.existsSync(svgMark)) {
    await makePngs(svgMark, 'mark');
  }

  // Generate PWA icons
  await makePwaIcons(squareSvg);

  // Generate favicon
  await makeFavicon(squareSvg);

  console.log('\n✅ All icons generated successfully!');
  console.log(`📁 Output directory: ${outDir}`);
})();
