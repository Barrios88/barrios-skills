#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const DEBUG_BORDER_COLORS = new Set(["00b0f0", "00bfff", "00ffff", "33ccff", "5ee7ff", "63e7ff", "66e7ff", "b6edff"]);
const DESIGN_PT_SCALE = 4 / 3;
const TEXTBOX_MIN_HEIGHT = 8;
const MULTILINE_HARD_LINE_HEIGHT = 10;
const MULTILINE_WARN_LINE_HEIGHT = 14;
const MAX_TEXT_FIT_SAMPLES = 20;
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const SLIDE_WIDTH = 1280;
const SLIDE_HEIGHT = 720;
const EDGE_MARGIN_PX = 48;
const HARD_EDGE_MARGIN_PX = 24;
const TIGHT_GAP_PX = 29;
const MAX_LAYOUT_SAMPLES = 20;
const MAX_RENDER_VERIFY_LOOPS = 3;
const CHARTISH_PATTERN =
  /\b(chart|graph|plot|axis|series|data label|bar chart|line chart|scatter|scatterplot|pie chart|donut chart|treemap|map chart|sparkline|trend line|trendline)\b/i;

function usage() {
  return `Usage: pro_deck_quality_check.js --pptx <file> --preview-dir <dir> --reference-dir <dir> --inspect <file> --report <file> [options]

Options:
  --allow-debug-color <hex>  May be repeated.
`;
}

function parseArgs(argv) {
  const args = { allowDebugColor: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const value = argv[i + 1];
    if (!value || value.startsWith("--")) throw new Error(`Missing value for ${arg}`);
    i += 1;
    if (arg === "--pptx") args.pptx = value;
    else if (arg === "--preview-dir") args.previewDir = value;
    else if (arg === "--reference-dir") args.referenceDir = value;
    else if (arg === "--inspect") args.inspect = value;
    else if (arg === "--report") args.report = value;
    else if (arg === "--allow-debug-color") args.allowDebugColor.push(value);
    else throw new Error(`Unknown option: ${arg}`);
  }
  for (const key of ["pptx", "previewDir", "referenceDir", "inspect", "report"]) {
    if (!args[key]) throw new Error(usage());
  }
  return args;
}

function runCapture(command, args, options = {}) {
  const result = spawnSync(command, args, {
    encoding: options.encoding,
    maxBuffer: options.maxBuffer || 80 * 1024 * 1024,
  });
  if (result.status !== 0) {
    const stderr = Buffer.isBuffer(result.stderr) ? result.stderr.toString("utf8") : result.stderr;
    const stdout = Buffer.isBuffer(result.stdout) ? result.stdout.toString("utf8") : result.stdout;
    throw new Error((stderr || stdout || `${command} ${args.join(" ")} failed`).trim());
  }
  return result.stdout;
}

function zipNames(pptxPath) {
  return String(runCapture("unzip", ["-Z1", pptxPath], { encoding: "utf8" }))
    .split(/\r?\n/)
    .filter(Boolean);
}

function zipListing(pptxPath) {
  const lines = String(runCapture("unzip", ["-l", pptxPath], { encoding: "utf8" })).split(/\r?\n/);
  const sizes = new Map();
  for (const line of lines) {
    const match = line.match(/^\s*(\d+)\s+\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}\s+(.+)$/);
    if (match) sizes.set(match[2], Number.parseInt(match[1], 10));
  }
  return sizes;
}

function readZipText(pptxPath, entryName) {
  return Buffer.from(runCapture("unzip", ["-p", pptxPath, entryName])).toString("utf8");
}

function readZipBuffer(pptxPath, entryName) {
  return Buffer.from(runCapture("unzip", ["-p", pptxPath, entryName]));
}

function slideNumber(entryName) {
  const match = entryName.match(/slide(\d+)\.xml$/);
  return match ? Number.parseInt(match[1], 10) : 0;
}

function numberedPngs(directory, prefixes) {
  if (!fs.existsSync(directory)) return [];
  return fs
    .readdirSync(directory)
    .filter((name) => {
      const lower = name.toLowerCase();
      return lower.endsWith(".png") && !lower.includes("contact-sheet") && prefixes.some((prefix) => lower.startsWith(prefix));
    })
    .sort()
    .map((name) => path.join(directory, name));
}

function inspectPptx(pptxPath, allowedDebugColors) {
  const result = {
    slide_count: 0,
    media_count: 0,
    chart_count: 0,
    chart_parts: [],
    embedded_workbook_count: 0,
    embedded_workbook_parts: [],
    slides_without_images: [],
    font_sizes_pt: [],
    raw_xml_font_sizes_pt: [],
    raw_min_font_pt: null,
    raw_max_font_pt: null,
    min_font_pt: null,
    max_font_pt: null,
    tiny_font_count: 0,
    low_body_font_count: 0,
    shrink_text_count: 0,
    debug_line_colors: [],
    zero_byte_media: [],
    invalid_png_media: [],
  };
  const names = zipNames(pptxPath);
  const sizes = zipListing(pptxPath);
  const slideXmlNames = names.filter((name) => /^ppt\/slides\/slide\d+\.xml$/.test(name)).sort((a, b) => slideNumber(a) - slideNumber(b));
  const mediaNames = names.filter((name) => name.startsWith("ppt/media/"));
  const chartNames = names.filter((name) => /^ppt\/(?:.*\/)?charts\/chart\d+\.xml$/.test(name)).sort();
  const embeddedWorkbookNames = names.filter((name) => /^ppt\/embeddings\/.*\.(xlsx|xlsm|bin)$/i.test(name)).sort();
  result.slide_count = slideXmlNames.length;
  result.media_count = mediaNames.length;
  result.chart_count = chartNames.length;
  result.chart_parts = chartNames;
  result.embedded_workbook_count = embeddedWorkbookNames.length;
  result.embedded_workbook_parts = embeddedWorkbookNames;

  for (const mediaName of mediaNames) {
    const size = sizes.get(mediaName) || 0;
    if (size === 0) {
      result.zero_byte_media.push(mediaName);
    } else if (mediaName.toLowerCase().endsWith(".png")) {
      const header = readZipBuffer(pptxPath, mediaName).subarray(0, 8);
      if (!header.equals(PNG_MAGIC)) result.invalid_png_media.push(mediaName);
    }
  }

  const suspiciousColors = new Set([...DEBUG_BORDER_COLORS].filter((color) => !allowedDebugColors.has(color)));
  for (const [idx, slideName] of slideXmlNames.entries()) {
    const slideNo = idx + 1;
    const xml = readZipText(pptxPath, slideName);
    if (!xml.includes("<a:blip")) result.slides_without_images.push(slideNo);
    result.shrink_text_count += (xml.match(/shrinkText/g) || []).length;
    for (const match of xml.matchAll(/\bsz="(\d+)"/g)) {
      const xmlPt = Number.parseInt(match[1], 10) / 100;
      result.raw_xml_font_sizes_pt.push(xmlPt);
      result.font_sizes_pt.push(xmlPt * DESIGN_PT_SCALE);
    }
    for (const lineMatch of xml.matchAll(/<a:ln\b[\s\S]*?<\/a:ln>/g)) {
      for (const colorMatch of lineMatch[0].matchAll(/<a:srgbClr\b[^>]*\bval="([0-9A-Fa-f]{6})"/g)) {
        const normalized = colorMatch[1].toLowerCase();
        if (suspiciousColors.has(normalized)) result.debug_line_colors.push({ slide: slideNo, color: normalized });
      }
    }
  }

  if (result.font_sizes_pt.length) {
    result.raw_min_font_pt = Math.min(...result.raw_xml_font_sizes_pt);
    result.raw_max_font_pt = Math.max(...result.raw_xml_font_sizes_pt);
    result.min_font_pt = Math.min(...result.font_sizes_pt);
    result.max_font_pt = Math.max(...result.font_sizes_pt);
    result.tiny_font_count = result.font_sizes_pt.filter((size) => size < 10).length;
    result.low_body_font_count = result.font_sizes_pt.filter((size) => size >= 10 && size < 14).length;
  }
  return result;
}

function textLineCount(text) {
  const value = String(text || "");
  if (!value.trim()) return 0;
  return Math.max(1, value.split(/\n/).length);
}

function textPreview(item) {
  return String(item.textPreview || item.text || "").replace(/\n/g, " | ").slice(0, 180);
}

function fitSample(item, lines, height, requiredHeight, reason) {
  return {
    slide: item.slide,
    id: item.id,
    textPreview: textPreview(item),
    textLines: lines,
    bbox: item.bbox,
    bbox_height: height,
    required_height: requiredHeight,
    reason,
  };
}

function checkTextboxFit(item, result) {
  const text = item.text || "";
  if (!String(text).trim()) return;
  const bbox = item.bbox;
  if (!Array.isArray(bbox) || bbox.length < 4) return;
  const height = Number.parseFloat(bbox[3]);
  if (!Number.isFinite(height)) return;
  let lines = Number.parseInt(item.textLines, 10);
  if (!Number.isFinite(lines)) lines = Math.max(1, String(text).split(/\n/).length);
  lines = Math.max(1, lines);

  let failure = null;
  let warning = null;
  if (height < TEXTBOX_MIN_HEIGHT) {
    const required = Math.max(TEXTBOX_MIN_HEIGHT, lines >= 2 ? lines * MULTILINE_HARD_LINE_HEIGHT : TEXTBOX_MIN_HEIGHT);
    failure = fitSample(item, lines, height, required, `nonempty textbox height is below ${TEXTBOX_MIN_HEIGHT}px`);
  } else if (lines >= 2 && height < lines * MULTILINE_HARD_LINE_HEIGHT) {
    failure = fitSample(item, lines, height, lines * MULTILINE_HARD_LINE_HEIGHT, `multiline textbox height is below ${MULTILINE_HARD_LINE_HEIGHT}px per line`);
  } else if (lines >= 2 && height < lines * MULTILINE_WARN_LINE_HEIGHT) {
    warning = fitSample(item, lines, height, lines * MULTILINE_WARN_LINE_HEIGHT, `multiline textbox height is below ${MULTILINE_WARN_LINE_HEIGHT}px per line`);
  }
  if (failure && result.text_fit_failures.length < MAX_TEXT_FIT_SAMPLES) result.text_fit_failures.push(failure);
  if (warning && result.text_fit_warnings.length < MAX_TEXT_FIT_SAMPLES) result.text_fit_warnings.push(warning);
}

function normalizedRole(item) {
  return String(item.role || "").toLowerCase();
}

function normalizedBbox(item) {
  const bbox = item.bbox;
  if (!Array.isArray(bbox) || bbox.length < 4) return null;
  const values = bbox.slice(0, 4).map((value) => Number.parseFloat(value));
  if (values.some((value) => !Number.isFinite(value))) return null;
  const [x, y, w, h] = values;
  if (w <= 0 || h <= 0) return null;
  return { x, y, w, h, right: x + w, bottom: y + h, area: w * h };
}

function textLayoutSample(item, extra = {}) {
  return {
    slide: item.slide,
    id: item.id,
    role: item.role,
    textPreview: textPreview(item),
    bbox: item.bbox,
    ...extra,
  };
}

function edgeMarginExempt(item) {
  const role = normalizedRole(item);
  return /\b(header|footer|source|caption|page|slide number|kicker)\b/.test(role);
}

function intersection(a, b) {
  const left = Math.max(a.x, b.x);
  const top = Math.max(a.y, b.y);
  const right = Math.min(a.right, b.right);
  const bottom = Math.min(a.bottom, b.bottom);
  const width = right - left;
  const height = bottom - top;
  if (width <= 0 || height <= 0) return null;
  return { left, top, width, height, area: width * height };
}

function overlapRatio(a, b, overlap) {
  return overlap.area / Math.min(a.area, b.area);
}

function axisGap(a, b, axis) {
  if (axis === "x") {
    if (a.right <= b.x) return b.x - a.right;
    if (b.right <= a.x) return a.x - b.right;
    return -1;
  }
  if (a.bottom <= b.y) return b.y - a.bottom;
  if (b.bottom <= a.y) return a.y - b.bottom;
  return -1;
}

function axisOverlap(a, b, axis) {
  if (axis === "x") return Math.min(a.right, b.right) - Math.max(a.x, b.x);
  return Math.min(a.bottom, b.bottom) - Math.max(a.y, b.y);
}

function analyzeTextLayout(textboxes, result) {
  const bySlide = new Map();
  for (const item of textboxes) {
    if (!String(item.text || "").trim()) continue;
    const bbox = normalizedBbox(item);
    if (!bbox) continue;
    const slideNo = Number.parseInt(item.slide, 10);
    if (!Number.isFinite(slideNo)) continue;
    if (!bySlide.has(slideNo)) bySlide.set(slideNo, []);
    bySlide.get(slideNo).push({ item, bbox });

    if (!edgeMarginExempt(item)) {
      const edgeViolations = [];
      const margins = [
        ["left", bbox.x],
        ["top", bbox.y],
        ["right", SLIDE_WIDTH - bbox.right],
        ["bottom", SLIDE_HEIGHT - bbox.bottom],
      ];
      const hardEdgeViolations = margins.filter(([, margin]) => margin < HARD_EDGE_MARGIN_PX).map(([side, margin]) => `${side} margin ${margin.toFixed(1)}px`);
      const softEdgeViolations = margins.filter(([, margin]) => margin >= HARD_EDGE_MARGIN_PX && margin < EDGE_MARGIN_PX).map(([side, margin]) => `${side} margin ${margin.toFixed(1)}px`);
      if (hardEdgeViolations.length && result.textbox_edge_failures.length < MAX_LAYOUT_SAMPLES) {
        result.textbox_edge_failures.push(textLayoutSample(item, { edgeViolations: hardEdgeViolations }));
      } else if (softEdgeViolations.length && result.low_margin_warnings.length < MAX_LAYOUT_SAMPLES) {
        result.low_margin_warnings.push(textLayoutSample(item, { edgeWarnings: softEdgeViolations }));
      }
    }
  }

  for (const items of bySlide.values()) {
    for (let i = 0; i < items.length; i += 1) {
      for (let j = i + 1; j < items.length; j += 1) {
        const a = items[i];
        const b = items[j];
        const overlap = intersection(a.bbox, b.bbox);
        if (overlap) {
          const ratio = overlapRatio(a.bbox, b.bbox, overlap);
          if (overlap.width >= 8 && overlap.height >= 12 && ratio >= 0.3 && result.textbox_overlap_failures.length < MAX_LAYOUT_SAMPLES) {
            result.textbox_overlap_failures.push({
              slide: a.item.slide,
              overlap,
              overlapRatio: Number(ratio.toFixed(3)),
              a: textLayoutSample(a.item),
              b: textLayoutSample(b.item),
            });
          }
          continue;
        }

        const horizontalGap = axisGap(a.bbox, b.bbox, "x");
        const verticalOverlap = axisOverlap(a.bbox, b.bbox, "y");
        if (horizontalGap >= 0 && horizontalGap < TIGHT_GAP_PX && verticalOverlap > Math.min(a.bbox.h, b.bbox.h) * 0.35) {
          if (result.tight_gap_warnings.length < MAX_LAYOUT_SAMPLES) {
            result.tight_gap_warnings.push({
              slide: a.item.slide,
              gapPx: Number(horizontalGap.toFixed(1)),
              orientation: "horizontal",
              a: textLayoutSample(a.item),
              b: textLayoutSample(b.item),
            });
          }
          continue;
        }

        const verticalGap = axisGap(a.bbox, b.bbox, "y");
        const horizontalOverlap = axisOverlap(a.bbox, b.bbox, "x");
        if (verticalGap >= 0 && verticalGap < TIGHT_GAP_PX && horizontalOverlap > Math.min(a.bbox.w, b.bbox.w) * 0.35) {
          if (result.tight_gap_warnings.length < MAX_LAYOUT_SAMPLES) {
            result.tight_gap_warnings.push({
              slide: a.item.slide,
              gapPx: Number(verticalGap.toFixed(1)),
              orientation: "vertical",
              a: textLayoutSample(a.item),
              b: textLayoutSample(b.item),
            });
          }
        }
      }
    }
  }
}

function inspectNdjson(inspectPath) {
  const result = {
    exists: fs.existsSync(inspectPath),
    line_count: 0,
    textbox_count: 0,
    text_chars: 0,
    image_count: 0,
    shape_count: 0,
    manual_chart_textbox_count: 0,
    manual_chart_textbox_samples: [],
    native_chart_record_count: 0,
    native_chart_record_samples: [],
    chartish_textbox_count: 0,
    chartish_textbox_samples: [],
    manual_chart_shape_count: 0,
    manual_chart_shape_samples: [],
    text_fit_failures: [],
    text_fit_warnings: [],
    textbox_overlap_failures: [],
    textbox_edge_failures: [],
    tight_gap_warnings: [],
    low_margin_warnings: [],
  };
  if (!result.exists) return result;
  const textboxes = [];
  for (const line of fs.readFileSync(inspectPath, "utf8").split(/\r?\n/)) {
    if (!line.trim()) continue;
    result.line_count += 1;
    let item;
    try {
      item = JSON.parse(line);
    } catch {
      continue;
    }
    if (item.kind === "chart") {
      result.native_chart_record_count += 1;
      if (result.native_chart_record_samples.length < MAX_LAYOUT_SAMPLES) {
        result.native_chart_record_samples.push({
          slide: item.slide,
          role: item.role,
          title: item.title,
          chartType: item.chartType,
          bbox: item.bbox,
        });
      }
    } else if (item.kind === "textbox") {
      result.textbox_count += 1;
      const text = item.text || "";
      result.text_chars += Number.parseInt(item.textChars, 10) || String(text).length;
      checkTextboxFit(item, result);
      const role = String(item.role || "");
      if (CHARTISH_PATTERN.test(role)) {
        result.manual_chart_textbox_count += 1;
        if (result.manual_chart_textbox_samples.length < MAX_LAYOUT_SAMPLES) result.manual_chart_textbox_samples.push(textLayoutSample(item));
      }
      if (CHARTISH_PATTERN.test(text)) {
        result.chartish_textbox_count += 1;
        if (result.chartish_textbox_samples.length < MAX_LAYOUT_SAMPLES) result.chartish_textbox_samples.push(textLayoutSample(item));
      }
      textboxes.push(item);
    } else if (item.kind === "image") {
      result.image_count += 1;
    } else if (item.kind === "shape") {
      result.shape_count += 1;
      const role = String(item.role || "");
      if (CHARTISH_PATTERN.test(role)) {
        result.manual_chart_shape_count += 1;
        if (result.manual_chart_shape_samples.length < MAX_LAYOUT_SAMPLES) {
          result.manual_chart_shape_samples.push({
            slide: item.slide,
            id: item.id,
            role: item.role,
            shapeType: item.shapeType || item.geometry,
            bbox: item.bbox,
          });
        }
      }
    }
  }
  analyzeTextLayout(textboxes, result);
  return result;
}

function inspectRenderVerifyLoops(verificationDir) {
  const result = {
    path: verificationDir ? path.join(verificationDir, "render_verify_loops.ndjson") : null,
    exists: false,
    loop_count: 0,
    latest_loop: null,
    latest_record: null,
  };
  if (!result.path || !fs.existsSync(result.path)) return result;
  result.exists = true;
  for (const line of fs.readFileSync(result.path, "utf8").split(/\r?\n/)) {
    if (!line.trim()) continue;
    let item;
    try {
      item = JSON.parse(line);
    } catch {
      continue;
    }
    if (item.kind !== "render_verify_loop") continue;
    result.loop_count += 1;
    const loop = Number.parseInt(item.loop, 10);
    if (Number.isFinite(loop)) result.latest_loop = loop;
    result.latest_record = { ...item };
    delete result.latest_record["render" + "QaPath"];
  }
  return result;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const pptxPath = path.resolve(args.pptx);
  const previewDir = path.resolve(args.previewDir);
  const referenceDir = path.resolve(args.referenceDir);
  const inspectPath = path.resolve(args.inspect);
  const reportPath = path.resolve(args.report);
  const verificationDir = path.join(path.dirname(inspectPath), "verification");
  const allowedDebugColors = new Set(args.allowDebugColor.map((value) => value.toLowerCase().replace(/^#/, "")));

  const failures = [];
  const warnings = [];
  if (!fs.existsSync(pptxPath)) {
    failures.push(`Missing PPTX: ${pptxPath}`);
    fs.mkdirSync(path.dirname(reportPath), { recursive: true });
    fs.writeFileSync(reportPath, `${JSON.stringify({ passed: false, failures, warnings }, null, 2)}\n`);
    console.log(reportPath);
    return 1;
  }

  const pptxMetrics = inspectPptx(pptxPath, allowedDebugColors);
  const referencePaths = numberedPngs(referenceDir, ["slide-"]);
  const previewPaths = numberedPngs(previewDir, ["slide-", "preview-"]);
  const inspectMetrics = inspectNdjson(inspectPath);
  const renderVerifyLoopMetrics = inspectRenderVerifyLoops(verificationDir);

  const slideCount = pptxMetrics.slide_count;
  if (slideCount < 1) failures.push("PPTX contains no slides.");
  if (!referencePaths.length) failures.push(`No art-plate reference images found in ${referenceDir}.`);
  else if (referencePaths.length !== slideCount) failures.push(`Reference art-plate count (${referencePaths.length}) does not match PPTX slide count (${slideCount}).`);
  if (previewPaths.length < slideCount) failures.push(`Preview image count (${previewPaths.length}) is below PPTX slide count (${slideCount}).`);
  if (pptxMetrics.slides_without_images.length) failures.push(`Slides without any embedded/generated/cropped image asset: ${JSON.stringify(pptxMetrics.slides_without_images)}.`);
  if (pptxMetrics.zero_byte_media.length) failures.push(`PPTX contains zero-byte media parts that PowerPoint cannot display: ${JSON.stringify(pptxMetrics.zero_byte_media.slice(0, 12))}.`);
  if (pptxMetrics.invalid_png_media.length) failures.push(`PPTX contains invalid PNG media parts: ${JSON.stringify(pptxMetrics.invalid_png_media.slice(0, 12))}.`);
  if (pptxMetrics.tiny_font_count) failures.push(`Found ${pptxMetrics.tiny_font_count} explicit text runs under 10pt.`);
  if (pptxMetrics.max_font_pt === null) failures.push("Could not find any explicit font sizes in PPTX XML.");
  else if (pptxMetrics.max_font_pt < 30) failures.push(`Largest explicit font is only ${pptxMetrics.max_font_pt.toFixed(1)}pt; title text should generally be >=30pt.`);
  if (pptxMetrics.debug_line_colors.length) failures.push(`Found suspicious debug-looking cyan/bright-blue line colors: ${JSON.stringify(pptxMetrics.debug_line_colors.slice(0, 12))}.`);
  if (!inspectMetrics.exists) failures.push(`Missing inspect artifact: ${inspectPath}.`);
  else if (inspectMetrics.textbox_count < Math.max(1, slideCount * 3)) failures.push(`Inspect artifact has only ${inspectMetrics.textbox_count} editable textboxes for ${slideCount} slides.`);
  else if (inspectMetrics.text_chars < 80) failures.push("Inspect artifact has too little editable text to represent the planned deck copy.");
  if (inspectMetrics.text_fit_failures.length) failures.push(`Found textbox fit failures that can render as clipped/hidden text: ${JSON.stringify(inspectMetrics.text_fit_failures.slice(0, 5))}.`);
  if (inspectMetrics.textbox_overlap_failures.length) failures.push(`Found severe textbox overlaps that can render as stacked or colliding text: ${JSON.stringify(inspectMetrics.textbox_overlap_failures.slice(0, 5))}.`);
  if (inspectMetrics.textbox_edge_failures.length) failures.push(`Found text boxes too close to slide edges outside exempt header/footer roles: ${JSON.stringify(inspectMetrics.textbox_edge_failures.slice(0, 5))}.`);
  if (!renderVerifyLoopMetrics.exists) failures.push(`Missing render/verify loop log: ${renderVerifyLoopMetrics.path}.`);
  else if (renderVerifyLoopMetrics.latest_loop > MAX_RENDER_VERIFY_LOOPS) failures.push(`Render/verify loop count exceeds ${MAX_RENDER_VERIFY_LOOPS}: ${renderVerifyLoopMetrics.latest_loop}.`);
  const manualChartRecordCount = inspectMetrics.manual_chart_shape_count + inspectMetrics.manual_chart_textbox_count;
  if (!pptxMetrics.chart_count && inspectMetrics.native_chart_record_count) {
    failures.push(
      `Inspect recorded ${inspectMetrics.native_chart_record_count} native chart objects, but the exported PPTX has no native chart XML parts (ppt/**/charts/chart*.xml). Verify chart export, not just builder-side chart helpers. Samples: ${JSON.stringify(inspectMetrics.native_chart_record_samples.slice(0, 5))}.`,
    );
  }
  if (!pptxMetrics.chart_count && manualChartRecordCount) {
    failures.push(
      `Found ${manualChartRecordCount} chart-like inspect records but no native PPTX chart XML parts (ppt/**/charts/chart*.xml). Use slide.charts.add(...) for data charts/graphs instead of drawing them manually. Text samples: ${JSON.stringify(inspectMetrics.manual_chart_textbox_samples.slice(0, 5))}. Shape samples: ${JSON.stringify(inspectMetrics.manual_chart_shape_samples.slice(0, 5))}.`,
    );
  }
  if (pptxMetrics.shrink_text_count) warnings.push(`Found ${pptxMetrics.shrink_text_count} shrinkText settings; confirm no rendered tiny text.`);
  if (pptxMetrics.low_body_font_count) {
    warnings.push(
      `Found ${pptxMetrics.low_body_font_count} explicit text runs from 10pt to under 14pt; confirm table/card/callout text feels natural and aesthetically balanced, not shrunken to fit density.`,
    );
  }
  if (inspectMetrics.text_fit_warnings.length) warnings.push(`Found tight textbox geometry; inspect rendered previews: ${JSON.stringify(inspectMetrics.text_fit_warnings.slice(0, 5))}.`);
  if (!pptxMetrics.chart_count && inspectMetrics.chartish_textbox_count) {
    warnings.push(
      `Found ${inspectMetrics.chartish_textbox_count} chart-like textbox copy samples but no native PPTX chart XML parts (ppt/**/charts/chart*.xml); confirm this deck truly has no chart/graph visual, otherwise use slide.charts.add(...). Samples: ${JSON.stringify(inspectMetrics.chartish_textbox_samples.slice(0, 5))}.`,
    );
  }
  if (inspectMetrics.tight_gap_warnings.length) warnings.push(`Found tight textbox spacing; inspect rendered previews: ${JSON.stringify(inspectMetrics.tight_gap_warnings.slice(0, 5))}.`);
  if (inspectMetrics.low_margin_warnings.length) warnings.push(`Found text boxes near the 0.5 inch edge margin; inspect rendered previews: ${JSON.stringify(inspectMetrics.low_margin_warnings.slice(0, 5))}.`);

  const report = {
    passed: failures.length === 0,
    failures,
    warnings,
    pptx: pptxPath,
    preview_dir: previewDir,
    reference_dir: referenceDir,
    inspect: inspectPath,
    metrics: {
      pptx: pptxMetrics,
      inspect: inspectMetrics,
      render_verify_loops: renderVerifyLoopMetrics,
      reference_count: referencePaths.length,
      preview_count: previewPaths.length,
    },
  };
  fs.mkdirSync(path.dirname(reportPath), { recursive: true });
  fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
  console.log(reportPath);
  if (failures.length) {
    failures.forEach((failure) => console.error(`FAIL: ${failure}`));
    return 1;
  }
  warnings.forEach((warning) => console.error(`WARN: ${warning}`));
  return 0;
}

try {
  process.exit(main());
} catch (error) {
  console.error(error.message || String(error));
  process.exit(1);
}
