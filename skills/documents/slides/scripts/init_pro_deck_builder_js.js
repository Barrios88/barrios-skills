#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

function usage() {
  return `Usage: init_pro_deck_builder_js.js --deck-id <slug> --output <file> --slide-count <n> --reference-dir <dir> --out-dir <dir> [--force]`;
}

function parseArgs(argv) {
  const args = { force: false };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--force") {
      args.force = true;
      continue;
    }
    if (!arg.startsWith("--")) throw new Error(`Unexpected positional argument: ${arg}`);
    const value = argv[i + 1];
    if (!value || value.startsWith("--")) throw new Error(`Missing value for ${arg}`);
    i += 1;
    if (arg === "--deck-id") args.deckId = value;
    else if (arg === "--output") args.output = value;
    else if (arg === "--slide-count") args.slideCount = Number.parseInt(value, 10);
    else if (arg === "--reference-dir") args.referenceDir = value;
    else if (arg === "--out-dir") args.outDir = value;
    else throw new Error(`Unknown option: ${arg}`);
  }
  for (const key of ["deckId", "output", "slideCount", "referenceDir", "outDir"]) {
    if (!args[key]) throw new Error(usage());
  }
  return args;
}

function cleanSlug(value) {
  const slug = String(value).trim().replace(/[^a-zA-Z0-9_-]+/g, "-").replace(/^-+|-+$/g, "").toLowerCase();
  return slug || "pro-deck-js";
}

function defaultSlides(count) {
  const slides = [];
  for (let idx = 1; idx <= count; idx += 1) {
    if (idx === 1) {
      slides.push({
        kicker: "PRO JS DECK",
        title: "Replace with deck title",
        subtitle: "Replace with a concise audience-facing framing sentence.",
        expectedVisual: "Title slide with generated art plate, prominent editable title/subtitle, and one core idea callout.",
        moment: "Replace with the core idea",
        notes: "Replace with presenter guidance for the cover.",
        sources: ["primary"],
      });
    } else if (idx % 3 === 0) {
      slides.push({
        kicker: `SECTION ${String(idx).padStart(2, "0")}`,
        title: `Replace slide ${idx} title`,
        subtitle: "Replace with the main claim this slide must support.",
        expectedVisual: `Slide ${idx} with editable metric cards and a visible text-free art-direction background.`,
        metrics: [
          ["00", "Replace metric label", "Replace source"],
          ["00", "Replace metric label", "Replace source"],
          ["00", "Replace metric label", "Replace source"],
        ],
        notes: "Replace with presenter guidance and caveats.",
        sources: ["primary"],
      });
    } else {
      slides.push({
        kicker: `SECTION ${String(idx).padStart(2, "0")}`,
        title: `Replace slide ${idx} title`,
        subtitle: "Replace with the main claim this slide must support.",
        expectedVisual: `Slide ${idx} with editable cards or diagram elements and a visible text-free art-direction background.`,
        cards: [
          ["Replace", "Add a specific, sourced point for this slide."],
          ["Author", "Create charts with native slide.charts.add(...); use editable geometry for cards, steps, and callouts."],
          ["Verify", "Render the preview, inspect it at readable size, and fix actionable layout issues within 3 total render loops."],
        ],
        notes: "Replace with presenter guidance and caveats.",
        sources: ["primary"],
      });
    }
  }
  return slides;
}

function artifactToolPackageFromNodeModules(directory) {
  if (!directory) return null;
  const nodeModulesDir = path.resolve(directory);
  const packageDir = path.join(nodeModulesDir, "@oai", "artifact-tool");
  const packageJsonPath = path.join(packageDir, "package.json");
  if (!fs.existsSync(packageJsonPath)) return null;
  try {
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, "utf8"));
    if (packageJson.name !== "@oai/artifact-tool") return null;
  } catch {
    return null;
  }
  return { nodeModulesDir, packageDir };
}

function defaultRuntimeNodeModules() {
  return path.join(
    os.homedir(),
    ".cache",
    "codex-runtimes",
    "codex-primary-runtime",
    "dependencies",
    "node",
    "node_modules",
  );
}

function nodeExecutableName() {
  return process.platform === "win32" ? "node.exe" : "node";
}

function resolveInstalledArtifactToolPackage() {
  return artifactToolPackageFromNodeModules(defaultRuntimeNodeModules());
}

function readPackageJson(packageDir) {
  try {
    return JSON.parse(fs.readFileSync(path.join(packageDir, "package.json"), "utf8"));
  } catch {
    return null;
  }
}

function isGeneratedArtifactToolPackage(packageDir) {
  const packageJson = readPackageJson(packageDir);
  return packageJson?.name === "@oai/artifact-tool" && packageJson?.main === "./index.ts";
}

function installArtifactToolPackageLink(outputPath, artifactPackage) {
  if (!artifactPackage) {
    throw new Error(
      [
        `Could not find @oai/artifact-tool in the default Codex runtime node_modules: ${defaultRuntimeNodeModules()}`,
        "Install or refresh the Codex runtime bundle, then retry.",
      ].join("\n"),
    );
  }

  const scopeDir = path.join(path.dirname(outputPath), "node_modules", "@oai");
  const target = path.join(scopeDir, "artifact-tool");
  fs.mkdirSync(scopeDir, { recursive: true });

  if (fs.existsSync(target)) {
    const stat = fs.lstatSync(target);
    if (stat.isSymbolicLink() || isGeneratedArtifactToolPackage(target)) {
      fs.rmSync(target, { recursive: true, force: true });
    } else {
      return { status: "existing", packageDir: target, nodeModulesDir: path.dirname(scopeDir) };
    }
  }

  let symlinkTarget = path.relative(scopeDir, artifactPackage.packageDir).split(path.sep).join("/");
  if (!symlinkTarget.startsWith(".")) symlinkTarget = `./${symlinkTarget}`;
  fs.symlinkSync(symlinkTarget, target, process.platform === "win32" ? "junction" : "dir");
  return { status: "linked", packageDir: artifactPackage.packageDir, nodeModulesDir: artifactPackage.nodeModulesDir };
}

function ensureBuilderModulePackage(outputPath) {
  const outputDir = path.dirname(outputPath);
  const packageJsonPath = path.join(outputDir, "package.json");
  if (fs.existsSync(packageJsonPath)) {
    const packageJson = readPackageJson(outputDir);
    return {
      packageJsonPath,
      status: packageJson?.type === "module" ? "existing-module" : "existing",
    };
  }
  fs.writeFileSync(
    packageJsonPath,
    `${JSON.stringify({ private: true, type: "module" }, null, 2)}\n`,
    "utf8",
  );
  return { packageJsonPath, status: "created" };
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!Number.isInteger(args.slideCount) || args.slideCount < 1) {
    throw new Error("--slide-count must be at least 1");
  }
  const skillDir = path.resolve(__dirname, "..");
  const templatePath = path.join(skillDir, "templates", "build_pro_deck_template.js");
  if (!fs.existsSync(templatePath)) throw new Error(`Missing template: ${templatePath}`);
  const outputPath = path.resolve(args.output);
  if (fs.existsSync(outputPath) && !args.force) {
    throw new Error(`${outputPath} already exists; pass --force to overwrite.`);
  }
  const rendered = fs
    .readFileSync(templatePath, "utf8")
    .replace("__DECK_ID_JSON__", JSON.stringify(cleanSlug(args.deckId)))
    .replace("__OUT_DIR_JSON__", JSON.stringify(path.resolve(args.outDir)))
    .replace("__REFERENCE_DIR_JSON__", JSON.stringify(path.resolve(args.referenceDir)))
    .replace("__SLIDES_JSON__", JSON.stringify(defaultSlides(args.slideCount), null, 2));
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, rendered, "utf8");
  const artifactPackage = resolveInstalledArtifactToolPackage();
  const packageLink = installArtifactToolPackageLink(outputPath, artifactPackage);
  const modulePackage = ensureBuilderModulePackage(outputPath);
  console.log(outputPath);
  if (packageLink?.status === "linked") {
    console.log(`Linked build/node_modules/@oai/artifact-tool to the default Codex runtime package at ${packageLink.packageDir}.`);
  } else if (packageLink?.status === "existing") {
    console.log(`Using existing build/node_modules/@oai/artifact-tool package at ${packageLink.packageDir}.`);
  }
  if (modulePackage.status === "created") {
    console.log(`Created ${modulePackage.packageJsonPath} with type=module for runtime Node execution.`);
  }
  console.log("Next: edit SLIDES/SOURCES and slide-specific layout functions, then run the builder with:");
  const runtimeNodePath = path.join(path.dirname(packageLink.nodeModulesDir), "bin", nodeExecutableName());
  if (runtimeNodePath && fs.existsSync(runtimeNodePath)) {
    console.log(`  ${runtimeNodePath} ${outputPath}`);
  } else {
    console.log(`  node ${outputPath}`);
  }
}

try {
  main();
} catch (error) {
  console.error(error.message || String(error));
  process.exit(1);
}
