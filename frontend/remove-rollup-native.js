// remove-rollup-native.js
const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, 'node_modules', 'rollup', 'dist', 'native.js');
if (fs.existsSync(filePath)) {
  fs.unlinkSync(filePath);
  console.log("✅ 'native.js' eliminado correctamente.");
} else {
  console.log("ℹ️ 'native.js' no existe. Continuando...");
}
