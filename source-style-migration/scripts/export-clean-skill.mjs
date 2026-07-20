#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const skillDir = path.resolve(scriptDir, "..");
const parentDir = path.dirname(skillDir);
const sourceName = path.basename(skillDir);

function timestampLabel(date = new Date()) {
  const pad = (value) => String(value).padStart(2, "0");
  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate())
  ].join("-");
}

function parseArgs(argv) {
  const args = {};
  for (const item of argv) {
    if (!item.startsWith("--")) continue;
    const [key, ...rest] = item.slice(2).split("=");
    args[key] = rest.length ? rest.join("=") : "true";
  }
  return args;
}

const args = parseArgs(process.argv.slice(2));
const targetDir = path.resolve(
  args.out || path.join(parentDir, `${sourceName}_dist_${timestampLabel()}`)
);

const excludedNames = new Set([
  ".DS_Store",
  "同事使用说明.md",
  "node_modules",
  "output",
  "material-spec-input",
  "material-spec-output",
  ".git",
  ".gitignore"
]);

const excludedRelativeDirs = new Set([
  "assets/material-renderer/assets/input",
  "assets/material-renderer/output"
]);

function shouldExclude(sourcePath) {
  const name = path.basename(sourcePath);
  if (excludedNames.has(name)) return true;
  const relative = path.relative(skillDir, sourcePath).split(path.sep).join("/");
  return excludedRelativeDirs.has(relative);
}

function copyClean(source, target) {
  if (shouldExclude(source)) return;
  const stat = fs.statSync(source);

  if (stat.isDirectory()) {
    fs.mkdirSync(target, { recursive: true });
    for (const entry of fs.readdirSync(source)) {
      copyClean(path.join(source, entry), path.join(target, entry));
    }
    return;
  }

  if (stat.isFile()) {
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.copyFileSync(source, target);
  }
}

function removeExcludedArtifacts(dir) {
  if (!fs.existsSync(dir)) return;
  for (const entry of fs.readdirSync(dir)) {
    const item = path.join(dir, entry);
    if (shouldExclude(item)) {
      fs.rmSync(item, { recursive: true, force: true });
      continue;
    }
    if (fs.statSync(item).isDirectory()) removeExcludedArtifacts(item);
  }
}

if (fs.existsSync(targetDir)) {
  throw new Error(`Target already exists: ${targetDir}`);
}

copyClean(skillDir, targetDir);
fs.mkdirSync(path.join(targetDir, "assets", "material-renderer", "assets"), { recursive: true });
removeExcludedArtifacts(targetDir);

console.log(`Exported clean skill: ${targetDir}`);
