#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");

const RULES = `
Create one polished 16:9 text-free art-direction plate for the slide described below.

Rules:
- Make it creative, professional, and presentation-ready as visual direction, not as a finished slide screenshot.
- Create a strictly text-free art plate: no readable titles, bullets, labels, numbers, dates, legends, table text, UI copy, logos, citations, or annotations.
- Use the plate to establish or follow a visual system: palette, atmosphere, motif, image treatment, icon style, density, and broad composition mood.
- Leave broad calm regions where deterministic editable PowerPoint objects can be authored later.
- Be mindful of the intended slide composition, aspect ratio, placement, and crop. If the final slide will place editable text on one side, compose the subject or focal object on the opposite side with calm negative space for that text.
- Use abstract placeholder strokes, unlabeled diagrams, soft panels, texture fields, collage areas, and broad hierarchy cues rather than exact text boxes that must be guessed later.
- Do not create dense precise grids of cards, boxes, UI panels, tables, or chart frames unless the final builder will author matching editable geometry from a separate layout map.
- Use at most one hero image or complex hero diagram per slide.
- For slides after slide 1, only make the image suitable as a full-slide background if it has clear, low-detail calm regions where foreground cards, titles, charts, and labels can sit without visual clash. Otherwise compose it as a side panel, hero frame, texture strip, or decorative accent with generous negative space.
- Include decorative or supporting visual material where useful: texture, atmosphere, motifs, contextual objects, cutaways, secondary details, and background depth. Do not make every slide depend on a single hero image.
- If icons appear, make them simple Lucide/Heroicons-style glyphs, not invented branded symbols.
- Vary layouts across slides; do not use left text / right image every time.
- Do not reuse the exact visual content from earlier slides unless the prompt explicitly calls for a repeated background, texture, or branded motif.
- Prefer lighter backgrounds unless the style guidance requests otherwise.
- Do not use "key insight" or "takeaway" pop-up boxes.
- Do not create a generic corporate blue slide unless the prompt specifically calls for it.
- Keep a clear authored-deck target in mind: the final deck will place editable cards, charts, callouts, labels, and text with deterministic PowerPoint geometry over or alongside this art plate.
- Hero/diagram/collage art should be easy to use as a full-slide background with fit: cover.
`.trim();

function usage() {
  return `Usage: prepare_reference_prompts.js <outline|-> [output_dir] --slide-count <n> [options]

Options:
  --style-guidance <text>
  --deck-size <WIDTHxHEIGHT>  default: 1280x720
  --force
`;
}

function parseArgs(argv) {
  const args = {
    outputDir: "tmp/slides/pro-reference-images",
    styleGuidance: "",
    deckSize: "1280x720",
    force: false,
  };
  const positionals = [];
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (!arg.startsWith("--")) {
      positionals.push(arg);
      continue;
    }
    if (arg === "--force") {
      args.force = true;
      continue;
    }
    const value = argv[i + 1];
    if (!value || value.startsWith("--")) throw new Error(`Missing value for ${arg}`);
    i += 1;
    if (arg === "--slide-count") args.slideCount = Number.parseInt(value, 10);
    else if (arg === "--style-guidance") args.styleGuidance = value;
    else if (arg === "--deck-size") args.deckSize = value;
    else throw new Error(`Unknown option: ${arg}`);
  }
  if (positionals.length < 1 || positionals.length > 2 || !args.slideCount) {
    throw new Error(usage());
  }
  args.outline = positionals[0];
  if (positionals[1]) args.outputDir = positionals[1];
  return args;
}

function loadOutline(source) {
  if (source === "-") return fs.readFileSync(0, "utf8");
  const maybePath = path.resolve(source);
  if (fs.existsSync(maybePath)) return fs.readFileSync(maybePath, "utf8");
  return source;
}

function ordinal(value) {
  const mod = value % 100;
  if (mod >= 11 && mod <= 13) return `${value}th`;
  return `${value}${{ 1: "st", 2: "nd", 3: "rd" }[value % 10] || "th"}`;
}

function parseSize(value) {
  const match = String(value).toLowerCase().match(/^\s*(\d+)x(\d+)\s*$/);
  if (!match) throw new Error(`Invalid --deck-size ${JSON.stringify(value)}; expected WIDTHxHEIGHT, for example 1280x720.`);
  const width = Number.parseInt(match[1], 10);
  const height = Number.parseInt(match[2], 10);
  if (width <= 0 || height <= 0) throw new Error("--deck-size dimensions must be positive.");
  return { width, height };
}

function extractSectionTitles(outline, total) {
  const paragraphs = outline
    .trim()
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .filter(Boolean);
  const titles = [];
  for (const paragraph of paragraphs.slice(1)) {
    const firstLine = paragraph.split(/\r?\n/)[0].trim();
    if (firstLine) titles.push(firstLine);
  }
  while (titles.length < total) titles.push(`Slide ${titles.length + 1}`);
  return titles.slice(0, total);
}

function buildSlidePrompt(index, total, outline, styleGuidance, titles, deckSize) {
  const titleHint = titles[index - 1] || `Slide ${index}`;
  const sectionSelector =
    `The outline begins with one intro paragraph, followed by exactly ${total} slide sections. ` +
    "Each slide section has one title line and one explanatory paragraph. " +
    `For this request, use only the ${ordinal(index)} slide section after the intro paragraph, ` +
    `whose semantic concept is "${titleHint}". ` +
    "Use that concept only for composition and visual subject matter; never render the title or any section text as readable text in the image. " +
    "Do not use neighboring sections' titles, facts, dates, or examples.";
  const styleBlock = styleGuidance.trim()
    ? `Apply this style guidance to palette, typography feel, layout, icon treatment, density, and tone:\n${styleGuidance.trim()}\n\n`
    : "";
  const role =
    index === 1
      ? "Create slide 1 as the visual system setter for the deck. Make it strong enough to guide later slides: clear blank title area, unlabeled visual thesis, and one memorable visual treatment."
      : `Create slide ${index} as a distinct slide that still belongs to the same deck visual system as slide 1. If the platform can use prior generated images as context, use slide 1 only as a style reference; do not reuse slide 1 content.`;
  return `${RULES}\n\n${role}\nTarget canvas: ${deckSize.width}x${deckSize.height} 16:9. If the image tool offers aspect controls, use a wide 16:9 composition.\n${sectionSelector}\n\n${styleBlock}Full outline:\n${outline}`;
}

function writeFileOnce(filePath, content, force) {
  if (fs.existsSync(filePath) && !force) {
    throw new Error(`${filePath} already exists; pass --force to overwrite.`);
  }
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, content, "utf8");
}

function writeManifest(outputDir, promptPaths, titles, deckSize) {
  const slides = promptPaths.map((promptPath, idx) => ({
    index: idx + 1,
    title: titles[idx] || `Slide ${idx + 1}`,
    prompt_path: promptPath,
    expected_image_path: path.join(outputDir, `slide-${String(idx + 1).padStart(2, "0")}.png`),
  }));
  const manifest = {
    reference_dir: outputDir,
    deck_size: deckSize,
    generation_mode: "platform-native-imagegen",
    instructions: [
      "Use the platform-native imagegen tool once per prompt.",
      "Do not display generated images in chat unless the user explicitly asks to review them.",
      "Generate slide 1 first as the visual style setter.",
      "For slides 2..N, use slide 1 as a style reference when the platform supports image context.",
      "Move or copy each selected generated image to its expected_image_path.",
      "Before finalizing the response, delete temporary imagegen files created during the run unless the user explicitly requested those image files as deliverables.",
    ],
    slides,
  };
  const manifestPath = path.join(outputDir, "reference_manifest.json");
  fs.writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");
  return manifestPath;
}

function writeMarkdown(outputDir, slides) {
  const lines = [
    "# Native Imagegen Prompts",
    "",
    "Use the platform-native imagegen tool for each prompt below. Save selected outputs to the listed filenames.",
    "Do not display generated images in chat unless the user explicitly asks to review them.",
    "Before finalizing the response, delete temporary imagegen files created during the run unless the user explicitly requested those image files as deliverables.",
    "",
  ];
  for (const slide of slides) {
    lines.push(`## Slide ${String(slide.index).padStart(2, "0")} -> ${slide.expectedImagePath}`);
    lines.push("");
    lines.push("```text");
    lines.push(slide.prompt);
    lines.push("```");
    lines.push("");
  }
  const markdownPath = path.join(outputDir, "imagegen_prompts.md");
  fs.writeFileSync(markdownPath, `${lines.join("\n")}\n`, "utf8");
  return markdownPath;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!Number.isInteger(args.slideCount) || args.slideCount < 1) throw new Error("--slide-count must be at least 1");

  const deckSize = parseSize(args.deckSize);
  const outline = loadOutline(args.outline);
  const titles = extractSectionTitles(outline, args.slideCount);
  const outputDir = path.resolve(args.outputDir);
  const promptsDir = path.join(outputDir, "prompts");
  const slides = [];
  const promptPaths = [];

  for (let index = 1; index <= args.slideCount; index += 1) {
    const prompt = buildSlidePrompt(index, args.slideCount, outline, args.styleGuidance, titles, deckSize);
    const promptPath = path.join(promptsDir, `slide-${String(index).padStart(2, "0")}.txt`);
    writeFileOnce(promptPath, `${prompt}\n`, args.force);
    promptPaths.push(promptPath);
    slides.push({
      index,
      prompt,
      expectedImagePath: path.join(outputDir, `slide-${String(index).padStart(2, "0")}.png`),
    });
  }

  const markdownPath = writeMarkdown(outputDir, slides);
  const manifestPath = writeManifest(outputDir, promptPaths, titles, deckSize);
  for (const promptPath of promptPaths) console.log(promptPath);
  console.log(markdownPath);
  console.log(manifestPath);
}

try {
  main();
} catch (error) {
  console.error(error.message || String(error));
  process.exit(1);
}
