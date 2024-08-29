// https://aur.archlinux.org/cgit/aur.git/tree/gen_preload.js?h=liteloader-qqnt-git
// https://github.com/LiteLoaderQQNT/LiteLoaderQQNT/blob/main/src/init.js

const fs = require("fs");
const path = require("path");

const outputPath = path.join(process.cwd(), "preloads");
const applicationPath = path.join(process.resourcesPath, "app", "application");

if (!fs.existsSync(outputPath)) {
    console.log("Creating %s...", outputPath);
    fs.mkdirSync(outputPath);
}

const applicationAsar = fs.readdirSync(applicationPath + ".asar", "utf-8");
for (const fileName of applicationAsar) {
    if (fileName.includes("preload")) {
        const filePath = path.join(applicationPath, fileName);
        const outputFilePath = path.join(outputPath, fileName);
        console.log("Extracting %s to %s", filePath, outputFilePath);
        const content = fs.readFileSync(filePath, "utf-8");
        fs.writeFileSync(
            outputFilePath, content,
            {encoding: "utf-8"}
        );
    }
}

process.exit(0);
