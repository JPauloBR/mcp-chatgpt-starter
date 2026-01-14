// Generate base64 data URLs for device images
const fs = require('fs');
const path = require('path');

const imagesDir = './src/att-device-details/images';
const files = fs.readdirSync(imagesDir).filter(f => f.endsWith('.png'));

let output = '// Auto-generated base64 image data\n\n';

for (const file of files) {
  const filePath = path.join(imagesDir, file);
  const data = fs.readFileSync(filePath);
  const base64 = data.toString('base64');
  const varName = file.replace('.png', '').replace(/-/g, '_');
  output += `export const ${varName} = "data:image/png;base64,${base64}";\n\n`;
}

console.log(output);
