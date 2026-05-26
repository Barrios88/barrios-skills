---
name: "Excel"
description: "Use this skill when a user requests to create, modify, analyze, visualize, or work with spreadsheet files (`.xlsx`, `.xls`, `.csv`, `.tsv`) with formulas, formatting, charts, tables, and recalculation."
---

# Spreadsheets skill

This skill includes guidelines for how to produce a correct, polished spreadsheet artifact quickly that completes the user's request. When producing spreadsheets or workbooks, you will be judged on layout, readability, style, adherence to industry norms/conventions and correctness. Follow the guidelines below for how to use the APIs effectively and how to verify your output before finalizing work for the user.

For complex, analytical, financial or research involved tasks, you are especially judged on correctness and quality. You need to be professional. For these, always make sure you have a plan for how you're organizing the spreadsheet, and the data or visualizations within each sheet. For business, finance, operations, dashboard, and data-analysis prompts, aim for an output that can compete with a strong analyst-built workbook, not just a functional grid. A good default shape is an executive summary or dashboard first, then source/assumptions, then model/detail sheets. For simpler tasks like a creating template or tracker, or things that do not require research, prioritize doing the spreadsheet build and edits quickly, while ensuring the user's request is fulfilled.

For additional stylistic best practices, follow: `style_guidelines.md`

# Tools + Contract
- Use the existing installed `@oai/artifact-tool` JS package which exists in the default Codex workspace dependencies node_modules for authoring, editing, inspecting, rendering, and exporting spreadsheet `.xlsx` workbooks. Use the bundled workspace Node.js and Python runtimes for local builders and helper scripts.
- Run builder files from a writable conversation-specific temp or workspace directory, not from the managed dependency directory.
- For JavaScript builders, do not use `NODE_PATH`; ensure bundled packages resolve through normal Node package lookup from the builder file.
- If needed, create a local `node_modules` directory link or Windows junction to the bundled `node_modules`; do not copy bundled dependency directories or import internal package files directly.
- Prefer to use a single executable JavaScript builder (.mjs); patch and rerun the same builder file when iterating. Do not put script bodies in shell heredocs or inline shell script bodies, or keep extra workspace-local builder copies.
- Final user-facing response: Must include a short summary of the workbook/sheets/ranges created or edited, plus standalone Markdown link(s) only to final `.xlsx` artifact(s), with this link format `[Revenue Model - model.xlsx](/absolute/path/to/model.xlsx)`; using a platform-appropriate absolute filesystem path. If there are multiple requested final workbooks, put each final `.xlsx` Markdown link on its own line. Do not wrap final artifact links in backticks or code fences, and do not put them in bullets, headings, or prose sentences.
- The final response summary must describe only the user-visible result. Do not mention implementation details such as `artifact_tool`, artifact-tool, `@oai/artifact-tool`, the Node/JS builder, copied builder scripts, package manifests, export workflow, verification workflow, rendered previews, or internal tooling unless explicitly requested.
- Do not link to or mention rendered previews, copied builder scripts, intermediate JSON/CSV/log files, scratch files, or other support artifacts unless explicitly requested. Do not delete or suppress support files just to satisfy this response rule.
- Do not use alternate workbook creation/editing libraries such as `openpyxl`, `xlsxwriter`, or `pandas.ExcelWriter` unless the user explicitly asks for a non-artifact-tool fallback.
- For analysis outside workbook authoring, use the simplest reliable installed tool. If analysis cannot be done directly in the JavaScript script or via formulas in the spreadsheet, additional Python libraries such as `pandas`/`numpy` are available in the bundled Python runtime in the default Codex workspace dependencies. Save analysis outputs as JSON/CSV; the JavaScript builder should read those files and create the workbook with `@oai/artifact-tool`. Keep workbook-derived or user-editable calculations as spreadsheet formulas when auditability or future editing matters.
- Use the update_plan tool to communicate your approach with the user and ensure you're staying on track to produce the best outcome for the user. Generally, your plan should emphasize speed to a correct first version, followed by incremental improvements and verification. Incrementally rendering your work and assessing overall aesthetics, formatting and correctness along the way is very important (you should rigorously inspect the output and be confident in quality), but do not get stuck in a long render-verify loop. As part of your plan, think about the best practices and conventions to follow for the specific type of spreadsheet you're creating and the best way to structure the workbook for readability and usability.

# General Rules
- Start meaningful edits quickly; avoid long upfront API exploration.
- Core APIs are listed in the API reference section below. Use them.
- If these skill instructions are already loaded in context, do not spend a shell turn re-reading this `SKILL.md` from disk. Move directly to the prompt, attachments, and workbook build.
- For workbook with multiple tabs/sheets, create/populate non-formula inputs/tables and sheets prior to populating cross-sheet formulas.

## Approach for quickly building a new spreadsheet
1. Setup: import `@oai/artifact-tool`, create workbook/sheets for new files.
2. Build quickly: bulk-write headers/data/formulas; then formatting/validation/conditional formatting; add charts/tables only when needed.
3. Use additional focused calls if helpful for streamed progress.
4. Near completion: inspect key ranges, scan formula errors, render all the sheets and verify, run a validation pass 
5. Export `.xlsx`

## Making edits on a spreadsheet
If a user asks to edit or add to an existing spreadsheet:
- For visual fix requests, start with the smallest plausible local change rather than applying sheet-wide autofit, wrapping, or restyling.
- When making edits, ensure existing formulas and patterns are consistent. For example, if asked to add another column or row to a table and there is conditional formatting applied to the whole table, it should extend to the new column or rows as well.
- If specific cells/rows/columns are specified in prompt, limit edits to those ranges unless a broader change is clearly necessary. The exceptions are when other parts of the spreadsheet depend on them, e.g. if there's a dynamic chart that is based on the range of values in a table and a new row is added, the chart should include that new row. Another example is if conditional formatting was already set for a table from A1:C5, and you add a new column D, the conditional formatting should be updated (or deleted and re-created) to cover A1:D5.
- For column resizing, avoid autofitting by default: instead, inspect only relevant data range, measure the longest text entry in that range, and set columnWidthPx to an estimated width based on text length (with a reasonable min/max cap). Use autofit only when the user explicitly asks for it.

## Handling queries and questions
- The user may ask questions about the sheet instead of requesting an edit or a change. Simply answer those questions about the spreadsheet based on the context available rather than making an edit the user didn't intend for. You can use inspect to learn more or directly read values/formulas/tables etc via accessor methods.

# Error Recovery
On first error:
1. Read error text.
2. Run one targeted `workbook.help("<exact_api>")` query only if needed.
3. Retry with minimal patch (not full rewrite).
4. Continue from existing workbook state.

Do not loop indefinitely on similar failures.

# Quality Guidelines
- Keep layout readable and bounded, contents visible:
  - avoid extreme width/height from unconstrained autofit
  - cap oversized widths/heights after `autofit` + `wrap_text`
- Prefer formula-driven logic over manual painted cells when logic is expected.
- Derived values must be formulas (not hardcoded) and legible.
- Use absolute/relative references correctly for fill/copy behavior.
- Do not use magic numbers in formulas; reference cells (e.g. `=H6*(1+$B$3)`).
- Blank editable templates must look blank/neutral before user data is entered. Count, ranking, best/worst, IRR/RATE/XIRR, variance, and status formulas should guard on required input cells and return `""`, `0`, or a clear "No entries yet" state as appropriate. Alternatively, prefill with a few rows of example data.
- Include at least one visual summary for tracker/planning requests when appropriate (KPI block, chart, dashboard area).
- For dashboard, visualization, chart-ready analysis, budget/reporting, trend, schedule/timeline, and KPI prompts with plottable data, include at least one native Excel chart unless a verified export failure remains after simplifying the chart. Do not silently replace all charts with styled tables.
- For presentation-ready analytical workbooks, plain range formatting alone is usually not enough. Prefer real Excel structures where useful: tables, freeze panes, filters, data validation, conditional formats, and at least one chart/KPI/dashboard visual when the prompt implies summary analysis.
- In rendered previews of dashboards and summary sheets, check financial values and row labels at normal zoom. Widen columns, adjust row heights, or move chart panels until important numbers and text are not clipped, awkwardly wrapped, or hidden.

# Completion Criteria
Complete only when:
- Workbook content is populated and formulas compute.
- No obvious formula errors in key scanned ranges (no bad refs/off-by-one/circular errors).
- `.xlsx` saved to `outputs/<unique_thread_id>/`.
- Layout is organized, legible, and aligned to request style (or default formatting baseline).

# Verification Rules
Before final response, verify values/formulas and visual quality.

1. Inspect key ranges:
```js
const check = await workbook.inspect({
  kind: "table",
  range: "Dashboard!A1:H20",
  include: "values,formulas",
  tableMaxRows: 20,
  tableMaxCols: 12,
});
console.log(check.ndjson);
```

Inspect targeting:
- Prefer sheet-qualified ranges (`"Sheet!A1:H20"`) or `sheetId`.

2. Scan formula errors:
```js
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);
```

3. Render sheets/ranges to verify visual output (skip if already verified and no style changes):
```js
const blob = await workbook.render({ sheetName: "Sheet1", range: "A1:H20", scale: 2 });
```
Make sure you do at least one visual pass of all the sheets in the workbook before the final export.

Visual requirements:
- Fix severe defects before finalizing: blank/broken charts, clipped key headers or numbers, unreadable colors, obvious formula errors, default blank sheets, or content outside the visible working area.
- Ensure logical labels or titles appear once, texts are all clearly visible, and merged ranges exist where labels or content intentionally span multiple columns.
- Do one focused visual repair pass after the initial render. Do not spend additional passes on minor polish once the workbook is correct, legible, and exported; note any minor limitation briefly and finalize.

4. Keep verification compact:
- Inspect key ranges.
- Avoid huge NDJSON dumps.

5. Export:
```js
await fs.mkdir(outputDir, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(`${outputDir}/output.xlsx`);
```

6. Finalize immediately after successful export + compact verification.
- Do not export extra `.xlsx` variants unless asked.
- Do not keep iterating on alternate designs once requirements are met, unless asked.

# Additional Instructions
Read the following templates instructions ONLY when a request relates to any of the following:
- Investment banking, company financial models, valuation, multi-statement forecasts, or source-backed financial filing analysis: templates/financial_models.md

Do not load these for other tasks that are unrelated unless the prompt explicitly asks for it.

# Source and PDF Extraction
- For PDF or 10-K/10-Q style inputs, can read PDF via python library `pypdf`, if available, then use one small structured extraction script to collect all required facts into a dict/JSON object. Avoid many ad hoc `rg`/`sed` passes over the same text.
- Keep source notes compact: record file name, section/table label, and enough context to audit the number. Do not paste large PDF excerpts into the workbook unless requested.

# Using artifact_tool APIs (JavaScript)

## Required Imports + Startup

Import existing workbook only when needed:
```js
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const input = await FileBlob.load("path/to/input.xlsx");
const workbook = await SpreadsheetFile.importXlsx(input);
```

Import CSV text directly when the source or intermediate data is CSV:
```js
import fs from "node:fs/promises";
import { Workbook } from "@oai/artifact-tool";

const csvText = await fs.readFile("path/to/input.csv", "utf8");
const workbook = await Workbook.fromCSV(csvText, { sheetName: "Sheet1" });
```
Prefer `Workbook.fromCSV(...)` over hand-parsing CSV rows; clean or analyze CSV with Python/Node first only when needed.

Create new workbook:
```js
import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const workbook = Workbook.create();
const sheet = workbook.worksheets.add("Inputs");
```

Final export:
```js
await fs.mkdir(outputDir, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(`${outputDir}/output.xlsx`);
```

## Build Rules
- Prefer block writes (`range.values`, `range.formulas`) over per-cell loops. Matrix shape must match the target range (for example `"D4:M4"` should be a 1x10 matrix, row x col).
- Seed scalar formulas once, then `fillDown()` / `fillRight()`. For dynamic-array formulas (`SEQUENCE`, `UNIQUE`, `FILTER`, `SORT`, `VSTACK`, `HSTACK`), write only the anchor cell and let the result spill after.
- Use `range.displayFormulas` plus `range.formulaInfos` when you need to understand a spill child or a data-table output cell.
- You do not need to call recalculate; calculation automatically happens.
- Date handling:
  - Prefer real `Date` objects for sortable/charted/formula date columns.
  - Apply date formats explicitly (for example `yyyy-mm-dd`).
- Use JSON-serializable values for non-Date cells: `string | number | boolean | null`.
- If a cell is intended to display literal text that begins with `=`, write it as a value prefixed with a single quote (for example `'=B2*C2`). This includes formula descriptions, validation examples, and labels; do not write these cells through `range.formulas`.
- Create every worksheet referenced by formulas before writing any cross-sheet formulas.
- When rebuilding dashboards, delete drawings first with `sheet.deleteAllDrawings()`. `range.clear()` does not remove charts, shapes, or images.
- Verify with `await workbook.inspect(...)`; use `workbook.help(...)` only when the quick surface below is insufficient.

## Conventions
- Use camelCase API names and option keys.
- Cell/range addressing: A1 notation (`sheet.getRange("A1:C10")`).
- Drawing anchors (`sheet.charts`, `sheet.shapes`, `sheet.images`): 0-based `{ row, col }`.
- Drawing offsets/extents use pixels (`rowOffsetPx`, `colOffsetPx`, `widthPx`, `heightPx`).

## Discovery Policy (Strict)
- Use this quick API surface first.
- Use `workbook.help(...)` only when blocked by uncertainty.
- For help queries, start with exact feature/path lookups (`chart`, `worksheet.getRange`, `worksheet.freezePanes`, `range.dataValidation`, `chart.series.add`). If an exact path fails, one broader wildcard search is allowed.
- Do not repeat semantically similar help queries.
- If one help query returns 0 matches, reformulate once, then proceed best-effort.
- `render` can be used to examine an existing workbook visually and for visual verifications.

Useful help calls:
```js
console.log(workbook.help("shape.add", { include: "examples,notes" }).ndjson);
console.log(
  workbook.help("*", {
    search: "fill|borders|autofit",
    include: "index,examples,notes",
    maxChars: 6000,
  }).ndjson,
);
```

## Reading existing/imported workbooks
- On existing/imported workbooks, get a compact summary via `inspect` to understand what already exists and where.
- Prefer `inspect(...)` for workbook understanding and discovery across broad areas.
- Prefer direct getters like `range.formulas` when you already know the target range and need the exact rectangular formula matrix.
- If formula locations are unknown, prefer `inspect({ kind: "formula", ... })` over reading `range.formulas` across a very large area.
- Prefer to set `maxChars`, `tableMaxRows`, `tableMaxCols`, and/or `maxResults` to prevent large dumps of data.

### Inspect for workbook understanding
- Compact summary:
```js
await wb.inspect({
  kind: "workbook,sheet,table",
  maxChars: 6000,
  tableMaxRows: 6,
  tableMaxCols: 6,
  tableMaxCellChars: 80,
});
```
- Quick overview of sheet ids and names: `await wb.inspect({ kind: "sheet", include: "id,name" })`
- Formula discovery in a targeted area: `await wb.inspect({ kind: "formula", sheetId: firstSheetName, range: "A1:Z30", maxChars: 2500, options: {maxResults:50} })`
- Checking existing styles in a targeted area: `await wb.inspect({ kind: "computedStyle", sheetId: firstSheetName, range: "A1:E10", maxChars: 2500 })`
- Common `kind` tokens: `workbook`, `sheet`, `table`, `region`, `match`, `formula`, `thread`, `computedStyle`, `definedName`, `drawing`
- Inspects can also be used to zoom in on specific areas, especially for target edits:
```js
await wb.inspect({
  kind: "region",
  sheetId: firstSheetName,
  range: "A1:Z30",
  maxChars: 2500,
});
```
- Inspect output may include JSON records with `"id"` values (for example `"ws/r5qsk5"`), which you can resolve back to workbook objects with `wb.resolve(...)`:
- `wb.resolve("ws/...")` -> worksheet
- `wb.resolve("th/...")` -> comment thread

## Additional feature-specific notes

### Merging cells
- Merging cells is useful for headers, dashboards, visual descriptors, and other multi-cell labels.
- If you plan to set a range of cells to a single value, consider merging those cells first.
For example:
```js
const range = sheet.getRange("I23:N24");
range.merge();
range.values = [["Some long description that should cross multiple cells"]];
```

## Known Gotchas (Do Not Repeat)
- Do not set undocumented attributes on remote objects.
- `Workbook.create()` starts with no sheets; add one before calling `getActiveWorksheet()`.
- Use matrix sizes that match target ranges unless you intentionally spill.
- If a formula appears unsupported, use an alternate equivalent.
- For cross-sheet formulas in a newly created workbook, create all referenced worksheets first, then write formulas. Avoid writing formulas that reference sheets that have not been added yet.
- Avoid full-column formula references such as `A:A`, `$A:$A`, or `Sheet!B:B`. Prefer bounded ranges sized to the editable table, e.g. `$A$6:$A$205`, especially inside `COUNTIFS`, `SUMIFS`, `INDEX`, and lookup formulas.
- If export fails, isolate the cause by checkpoint-exporting after each major feature block: base sheets, values/formulas, formatting, conditional formatting, tables, charts/rendering. Do this before rewriting the workbook.
- If export fails with `invalid int32: NaN` or another serialization error after formatting or charts, do not rerun the same script unchanged. First remove or simplify optional drawing/chart/style details in this order: nested/custom border configs, custom chart axis/style mutations, broad row/column formatting/autofit calls, then nonessential drawings. Preserve values/formulas and keep or retry a minimal helper-range chart when the prompt needs charts; only drop all charts/drawings if the simplified chart still prevents export.
- Prefer fills, font hierarchy, spacing, and section bands over complex nested border objects. If you use borders, start with a minimal preset or a very simple thin/light border on a bounded range and checkpoint export before applying borders widely. Avoid nested `inside`/`around`/`outline` border configs and border `weight` settings unless you have already checkpoint-exported that exact pattern successfully.
- For chart-heavy dashboards, checkpoint export after the first basic helper-range chart before adding multiple charts or optional axis/formatting mutations. If a chart export failure happens twice, keep the cleanest minimal chart that exports or replace the failing chart with a clearly labeled helper table/KPI block rather than spending the task on repeated chart debugging.
- Keep formatting and formulas on bounded ranges. Avoid whole-row or whole-column formatting/autofit for generated workbooks unless you have verified the export immediately afterward.

## Quick API Surface (High-Value + Common)

### Core workbook/file APIs
- `import { FileBlob, SpreadsheetFile, Workbook } from "@oai/artifact-tool"`
- `const workbook = Workbook.create(); const sheet = workbook.worksheets.add("Sheet1")`
- `const workbook = await SpreadsheetFile.importXlsx(arrayBufferOrFileBlob)`
- `const xlsx = await SpreadsheetFile.exportXlsx(workbook); await xlsx.save("output.xlsx")`
- `const inspect = await workbook.inspect({ kind: "sheet", include: "id,name", sheetId, range: "A1:C10" })`
- `const help = workbook.help("worksheet.getRange", { include: "index,examples" })`
- Preferred: `const blob = await workbook.render({ sheetName: "Sheet1", autoCrop: "all", scale: 1, format: "png" })`
- To get the bytes and/or save the blob to file: 
```js
const previewBytes = new Uint8Array(await preview.arrayBuffer()); 
await fs.writeFile(`${outputDir}/preview.png`, previewBytes);
```
- `const workbook = await Workbook.fromCSV(csvText, { sheetName: "Sheet1" })`
- `await workbook.fromCSV(csvText, { sheetName: "ImportedData" })`

### Worksheet selection/creation
- `workbook.worksheets.add(name)`
- `workbook.worksheets.getItem(name)`
- `workbook.worksheets.getOrAdd(name, { renameFirstIfOnlyNewSpreadsheet: true })`
- `workbook.worksheets.getItemAt(index)`
- `workbook.worksheets.getActiveWorksheet()` (only after at least one sheet exists)

### Worksheet operations
- `sheet.getRange("A1:C10")`, `sheet.getRangeByIndexes(startRow, startCol, rowCount, colCount)`, `sheet.getCell(row, col)`
- `sheet.getUsedRange(valuesOnly?)`
- `sheet.mergeCells("A1:C1")`, `sheet.unmergeCells("A1:C1")`
- `sheet.freezePanes.freezeRows(1)`, `sheet.freezePanes.freezeColumns(2)`, `sheet.freezePanes.unfreeze()`
- `sheet.tables`, `sheet.charts`, `sheet.sparklineGroups` (`sheet.sparklines` alias), `sheet.shapes`, `sheet.images`
- `sheet.showGridLines = false`
- `sheet.dataTables`, `sheet.conditionalFormattings`, `sheet.dataValidations`
- `sheet.deleteAllDrawings()` removes charts, shapes, and images before a dashboard rebuild.

### Range values/formulas
- `const range = sheet.getRange("A1:C10")`
- `range.values = [[...], ...]` (2D matrix of values)
- `range.formulas = [["=..."], ...]`
- `range.formulasR1C1 = [["=RC[-1]*2"]]`
- To read: `range.values` / `range.formulas` / `range.displayFormulas` / `range.formulaInfos` (for spill/array formulas)
- `range.write(matrixOrPayload)` (auto-sizes/spills from anchor as needed)
- `range.writeValues(matrixOrRows)`
- `range.fillDown()`, `range.fillRight()`
  - `sheet.getRange("D2").formulas = [["=..."]]`
  - `sheet.getRange("D2:D200").fillDown()`
- `range.clear({ applyTo: "contents" | "formats" | "all" })`
- `range.copyFrom(sourceRange, "values" | "formulas" | "all")` source and destination must have the same shape
- `range.copyTo(destRange, "values" | "formulas" | "all")`
- `range.offset(...)`, `range.resize(...)`, `range.getCurrentRegion()`, `range.getRow(i)`, `range.getColumn(j)`
- `range.getRangeByIndexes(...)`, `range.getCell(...)`
- `range.merge()`, `range.merge(true)` to merge across, `range.unmerge()`

### Formatting
- `range.format` supports `fill`, `font`, `numberFormat`, `borders`, alignments, `wrapText`
- `range.format.autofitColumns()`, `range.format.autofitRows()`
- `range.format.columnWidth = 18`, `range.format.rowHeight = 24`
- `range.format.columnWidthPx = 120`, `range.format.rowHeightPx = 24`
- `range.setNumberFormat("yyyy-mm-dd")`
- `range.format.numberFormat = [["0"], ["0.00"], ["@"]]`

### Validation + conditional formatting
- `range.dataValidation = { rule: { type: "list", formula1: "Categories!$A$2:$A$4" } }`
- `range.dataValidation = { rule: { type: "list", values: ["Not Started", "In Progress"] } }`
- `sheet.dataValidations.add({ range: "B2:B100", rule: { type: "whole", operator: "between", formula1: 1, formula2: 10 } })`
- `range.conditionalFormats.add(type, config)`
- `range.conditionalFormats.addCustom(formula, format)`
- `range.conditionalFormats.addCellIs({...})`
- `range.conditionalFormats.addDataBar({...})`
- `range.conditionalFormats.addColorScale({...})`
- `range.conditionalFormats.deleteAll()` / `range.conditionalFormats.clear()`
- `sheet.conditionalFormattings.add({ range, rule })`

```js
const r = sheet.getRange("B2:B20");
r.conditionalFormats.addCellIs({
  operator: "lessThan",
  formula: 0,
  format: { font: { color: "#DC2626" } },
});
r.conditionalFormats.addCustom("=B2<0", { fill: "#FECACA" });
r.conditionalFormats.addColorScale({
  minColor: "#FEE2E2",
  midColor: "#FEF3C7",
  maxColor: "#DCFCE7",
});
r.conditionalFormats.addDataBar({ color: "accent5", gradient: true });
```

### Tables
- Rules: When adding new tables, set explicit unique names (`TasksTable`, `SummaryTable`).
- You cannot have multiple tables over the same range. Before adding a table on an existing/imported workbook, confirm the target range does not already overlap an existing table. Prefer the initial compact `inspect` summary over a separate tables-only scan when available.
- `const table = sheet.tables.add("A1:H200", true, "TasksTable")`
- `table.rows.add(null, [[...], ...])`, `table.getDataRows()`, `table.getHeaderRowRange()`
- Read tables: `sheet.tables.items` -> `Table[]`
- Set + Getters: `table.name`, `table.style`, `table.style`, `table.showHeaders`
- Toggles for table utilities (set/get): `table.showTotals`, `table.showBandedColumns = true`, `table.showFilterButton`
- `table.delete()`

### Charts
- Rules: When adding or moving charts, do not cover existing data. Put charts in a reserved rectangle with blank gutter columns/rows around the chart area.
- Fast chart path, no help lookup needed for common line/bar/scatter charts: write a compact helper range with text categories and one column per series, then chart that range.
```js
sheet.getRange("F4:H7").values = [
  ["Month", "Revenue", "EBITDA"],
  ["Jan", 100, 10],
  ["Feb", 120, 18],
  ["Mar", 130, 22],
];
const chart = sheet.charts.add("line", sheet.getRange("F4:H7"));
chart.setPosition("J4", "Q20");
chart.title = "Revenue and EBITDA Trend";
chart.hasLegend = true;
chart.xAxis = { axisType: "textAxis" };
chart.yAxis = { numberFormatCode: "$#,##0" };
```
- Fast chart path from range: `const chart = sheet.charts.add("line", sourceRange)` when the source range already has headers and text x-axis labels.
- Avoid manual `chart.series.add(...)` and `chart.legend = {...}` on the first pass, unless source-range based chart creation does not work (for example, non-continuous data). Use a helper range chart first, then add optional chart styling only if the basic chart renders and exports cleanly.
- If you want to set specific chart props after the helper-range path is not enough: `const chart = sheet.charts.add("bar", chartProps)`, then checkpoint export before adding optional styling.
- If using compat positioning, always set position: `chart.setPosition("F2", "M20")`.
- `sheet.charts.getItemOrNullObject("Chart 1")`, `sheet.charts.deleteAll()`
- To update x/y-axis, prefer compact config assignments such as `chart.xAxis = { axisType: "textAxis", tickLabelInterval: 2 }` and `chart.yAxis = { numberFormatCode: "$#,##0" }`. These help legibility and visibility.
- For month/date x-axes, prefer a chart helper range with text labels such as `Jan 2025` or `2025-01`. Do not rely on date axis number formats alone; rendered previews can show Excel serial numbers.
- Chart types: `"bar" | "line" | "area" | "pie" | "doughnut" | "scatter" | "bubble" | "radar" | "stock" | "treemap" | "sunburst" | "histogram" | "boxWhisker" | "waterfall" | "funnel" | "map"`.

### Sparklines
- `sheet.sparklines.add({...})`, `sheet.sparklines.clear()`, `sheet.sparklines.deleteAll()` (`sheet.sparklineGroups` is the worksheet-scoped alias)

### Help / Grep
Use `workbook.help(...)` primarily for obscure/advanced surfaces (for example deep chart axis settings, unusual drawing configs, pivot APIs, or uncommon option schemas).
- `workbook.help("enum.ShapeGeometry", { include: "index,notes" }).ndjson`
- `workbook.help("enum.*", { search: "ShapeGeometry|LineStyle", include: "index" }).ndjson`
- `workbook.help("shape.add", { include: "examples,notes" }).ndjson`
- `workbook.help("*", { search: "fill|borders|autofit", include: "index,examples,notes", maxChars: 6000 }).ndjson`


### JavaScript example snippet (runnable)

```js
import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

async function quickApiExample() {
  const workbook = Workbook.create();
  var sheet = workbook.worksheets.add("ExampleSheet");

  sheet = workbook.worksheets.getItem("ExampleSheet");
  sheet.getRange("A1:D4").values = [
    ["Name", "Personality Type", "Age", "Birthday"],
    ["John Doe", "Introvert", 30, new Date("1990-01-01T00:00:00Z")],
    ["Jane Smith", "Extrovert", 25, new Date("1995-02-15T00:00:00Z")],
    ["Jim Very Long Name", "Ambivert", 40, new Date("1980-03-20T00:00:00Z")],
  ];
  sheet.getRange("E1").values = [["Score"]];
  sheet.getRange("E2").formulas = [["=C2*10"]]; // score is 10 * age
  sheet.getRange("E2:E10").fillDown();
  const headerRange = sheet.getRange("A1:E1");

  // Styling
  const headerFormats = {
    fill: "#0F766E",
    font: { bold: true, color: "#FFFFFF" },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    rowHeight: 16,
  };
  headerRange.format = headerFormats;
  headerRange.format.autofitColumns();

  const dataRange = sheet.getRange("A2:D10");
  dataRange.format.wrapText = true;
  sheet.showGridLines = false;

  // Format dates properly.
  sheet.getRange("D2:D10").format.numberFormat = "MM/DD/YYYY";

  // Conditional formatting
  sheet.getRange("C2:C10").conditionalFormats.addDataBar({
    color: "#704023",
    gradient: true,
  });
  sheet.getRange("E2:E10").conditionalFormats.add("cellIs", {
    operator: "greaterThan",
    formula: 300,
    format: { font: { color: "#B91C1C" } },
  });
  sheet.conditionalFormattings.add({
    range: "B2:B10",
    rule: {
      type: "expression",
      formula: '=B2="Introvert"',
      format: { fill: "#FCA5A5" },
    },
  });

  // Data validation: Since Personality Type is a dropdown category, add data validation.
  sheet.getRange("B2:B10").dataValidation = {
    rule: {
      type: "list",
      values: ["Introvert", "Extrovert", "Ambivert"],
      // formula1: "CategoriesSheet!$A$2:$A$4", // Alternative: reference a tunable list
    },
  };

  // Tables: Turn it into a table (for example purposes! Make sure table names are unique)
  // NOTE: If hasHeaders=true, the range must include the header row.
  const table = sheet.tables.add("A1:E10", true, "PeopleTable");
  table.getHeaderRowRange();

  // First column is still wide since we only auto-fit the first row. Expand it manually.
  sheet.getRange("A1:A10").format.columnWidth = 20;

  // Create charts to the right of the table
  sheet.getRange("H1:O1").merge();
  sheet.getRange("H1").values = [["Charts"]];
  sheet.getRange("H1").format = headerFormats;

  // Adding charts
  const chart = sheet.charts.add("bar", {
    from: { row: 1, col: 7 },
    extent: { widthPx: 620, heightPx: 320 },
  });
  chart.title = "Person by Scores";
  chart.hasLegend = true;
  chart.displayBlanksAs = "zero";
  chart.legend.position = "right";
  chart.barOptions.direction = "column";
  chart.barOptions.grouping = "clustered";
  const sheetRef = sheet.name.replaceAll("'", "''");
  const dataEndRow = 4; // Keep chart refs to rows with data only.

  const scoreSeries = chart.series.add("Scores by Person");
  scoreSeries.categoryFormula = `'${sheetRef}'!$A$2:$A$${dataEndRow}`;
  scoreSeries.formula = `'${sheetRef}'!$E$2:$E$${dataEndRow}`;
  scoreSeries.valuesFormatCode = "0";
  chart.setPosition("H2", "O16");

  // Granular control over chart axes
  chart.xAxis = {
    axisType: "textAxis",
    title: { text: "Person", textStyle: { fontSize: 13, bold: true } },
    position: "bottom",
    orientation: "minMax",
    textStyle: { fontSize: 10 },
  };
  chart.yAxis = {
    axisType: "textAxis",
    title: { text: "Scores", textStyle: { fontSize: 13, bold: true } },
    numberFormatCode: "0,000",
    numberFormatSourceLinked: false,
  };

  // Chart 2 - Fastest path with defaults
  const chart2 = sheet.charts.add("line", sheet.getRange("B2:C4"));
  chart2.title = "Scores by Personality";
  chart2.setPosition("H20", "O35");

  // Sparklines: add to the right of table
  const sparklinesHeader = sheet.getRange("F1");
  sparklinesHeader.values = [["Sparklines"]];
  sparklinesHeader.format = headerFormats;
  sparklinesHeader.format.autofitColumns();

  sheet.sparklines.add({
    type: "column", // "line" | "column" | "stacked"
    sourceData: sheet.getRange("E2:E10"),
    targetRange: sheet.getRange("F2:F10"),
    seriesColor: "#AAAAAA",
  });

  // Render
  await fs.mkdir("output", { recursive: true });
  const pngBlob = await workbook.render({
    sheetName: "ExampleSheet",
    autoCrop: "all",
    scale: 1,
    format: "png",
  });
  const pngBytes = new Uint8Array(await pngBlob.arrayBuffer());
  await fs.writeFile("output/example_sheet.png", pngBytes);
  console.log("Rendered first sheet to 'output/example_sheet.png'");

  // Export
  const out = "output/example_sheet.xlsx";
  const xlsx = await SpreadsheetFile.exportXlsx(workbook);
  await xlsx.save(out);
}

await quickApiExample();
```

Render:
```js
const imageBlob = await workbook.render({
  sheetName: "ExampleSheet",
  autoCrop: "all",
  scale: 1,
  format: "png",
});
```

Export:
```js
const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save("output/spreadsheet.xlsx");
```
