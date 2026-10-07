// tiny build step: copy public/ into dist/ (keeps the multi-stage Node build honest)
const fs = require("fs");
const path = require("path");
const src = path.join(__dirname, "public");
const dst = path.join(__dirname, "dist");
fs.rmSync(dst, { recursive: true, force: true });
fs.mkdirSync(dst, { recursive: true });
for (const f of fs.readdirSync(src)) fs.copyFileSync(path.join(src, f), path.join(dst, f));
console.log("built:", fs.readdirSync(dst).join(", "));
