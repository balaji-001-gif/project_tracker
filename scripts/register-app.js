// Registers the app in sites/apps.txt during yarn postinstall
// This works around a Frappe v15 bench bug where bench build --app runs
// before the app is added to apps.txt, causing esbuild to crash with
// "paths[0] must be of type string" because get_public_path() returns undefined.

const fs = require("fs");
const path = require("path");

// From the app root (apps/project_tracker/), apps.txt is at ../../sites/apps.txt
const appsTxtPath = path.resolve(process.cwd(), "..", "..", "sites", "apps.txt");

if (!fs.existsSync(appsTxtPath)) {
  console.log("sites/apps.txt not found, skipping registration");
  process.exit(0);
}

const content = fs.readFileSync(appsTxtPath, "utf-8");
const appName = "project_tracker";

if (!content.includes(appName)) {
  fs.appendFileSync(appsTxtPath, `\n${appName}`);
  console.log(`✓ Registered ${appName} in sites/apps.txt`);
} else {
  console.log(`✓ ${appName} already registered in sites/apps.txt`);
}
