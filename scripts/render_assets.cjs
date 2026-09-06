const fs = require('node:fs');
const path = require('node:path');
const sharp = require('sharp');
const root = path.resolve(__dirname, '..');
async function main() {
  const directory = path.join(root, 'diagrams');
  const files = fs.readdirSync(directory).filter(n => n.endsWith('.svg')).sort();
  for (const filename of files) {
    const svg = path.join(directory, filename);
    await sharp(svg, {density: 144}).png().toFile(svg.replace(/\.svg$/, '.png'));
    console.log(filename);
  }
}
main().catch(e => { console.error(e); process.exitCode = 1; });
