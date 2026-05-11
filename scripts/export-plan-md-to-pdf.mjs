/**
 * Export a Cursor plan .md to PDF with VS Code–like preview styling.
 * Renders Mermaid blocks to PNG via @mermaid-js/mermaid-cli, then md-to-pdf.
 * Work dir is always ASCII-only (under repo) to avoid Windows/Chromium path issues.
 */
import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync, copyFileSync } from "fs";
import { dirname, join, basename } from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";
import { randomBytes } from "crypto";

const __dirname = dirname(fileURLToPath(import.meta.url));

const SRC = process.argv[2];
const OUT = process.argv[3];
if (!SRC || !OUT) {
  console.error("Usage: node export-plan-md-to-pdf.mjs <source.md> <output.pdf>");
  process.exit(1);
}

const slug = randomBytes(4).toString("hex");
const workDir = join(__dirname, "..", ".tmp_plan_pdf", slug);
if (existsSync(workDir)) rmSync(workDir, { recursive: true });
mkdirSync(workDir, { recursive: true });

let md = readFileSync(SRC, "utf8");

if (md.startsWith("---")) {
  const end = md.indexOf("\n---\n", 3);
  if (end !== -1) {
    const front = md.slice(3, end).trim();
    md =
      "> **计划元数据（YAML 已展开为引用块，便于阅读）**\n>\n" +
      front
        .split("\n")
        .map((l) => "> " + l)
        .join("\n") +
      "\n\n---\n\n" +
      md.slice(end + 5);
  }
}

const mermaidRe = /```mermaid\n([\s\S]*?)```/g;
let idx = 0;
md = md.replace(mermaidRe, (_, code) => {
  idx += 1;
  const mmdPath = join(workDir, `diagram-${idx}.mmd`);
  const pngPath = join(workDir, `diagram-${idx}.png`);
  writeFileSync(mmdPath, code.trim() + "\n", "utf8");
  execSync(
    `npx --yes @mermaid-js/mermaid-cli -i diagram-${idx}.mmd -o diagram-${idx}.png -b white -w 1400`,
    { stdio: "inherit", cwd: workDir, shell: true, env: process.env }
  );
  return `\n![流程图 ${idx}](diagram-${idx}.png)\n`;
});

const bodyPath = join(workDir, "body.md");
writeFileSync(bodyPath, md, "utf8");

const cssPath = join(workDir, "vscode-preview.css");
writeFileSync(
  cssPath,
  `
@page { margin: 18mm 16mm; }
html, body {
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe WPC", "Segoe UI", "Helvetica Neue", "Microsoft YaHei UI", "Microsoft YaHei", sans-serif;
  font-size: 14px;
  line-height: 1.65;
  color: #333333;
  background: #ffffff;
  max-width: 860px;
  margin: 0 auto;
  padding: 12px 8px 48px;
}
h1 { font-size: 1.85em; font-weight: 600; margin: 0.7em 0 0.4em; border-bottom: 1px solid #eaecef; padding-bottom: 0.25em; }
h2 { font-size: 1.45em; font-weight: 600; margin: 1.1em 0 0.45em; }
h3 { font-size: 1.2em; font-weight: 600; margin: 1em 0 0.4em; }
h4 { font-size: 1.05em; font-weight: 600; margin: 0.9em 0 0.35em; }
p { margin: 0.55em 0; }
a { color: #0366d6; text-decoration: none; }
a:hover { text-decoration: underline; }
ul, ol { padding-left: 1.6em; margin: 0.5em 0; }
li { margin: 0.25em 0; }
blockquote {
  margin: 0.6em 0;
  padding: 0.35em 0.9em;
  border-left: 4px solid #dfe2e5;
  color: #57606a;
  background: #f6f8fa;
}
code {
  font-family: "Cascadia Code", "SF Mono", Consolas, "Liberation Mono", Menlo, monospace;
  font-size: 0.92em;
  background: rgba(175, 184, 193, 0.22);
  padding: 0.15em 0.35em;
  border-radius: 4px;
}
pre {
  background: #f6f8fa;
  border: 1px solid #e1e4e8;
  border-radius: 6px;
  padding: 12px 14px;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.5;
}
pre code { background: transparent; padding: 0; font-size: inherit; }
table {
  border-collapse: collapse;
  width: 100%;
  margin: 0.8em 0;
  font-size: 13px;
}
th, td {
  border: 1px solid #dfe2e5;
  padding: 8px 12px;
  text-align: left;
  vertical-align: top;
}
th { background: #f6f8fa; font-weight: 600; }
tr:nth-child(even) td { background: #fafbfc; }
hr {
  border: none;
  border-top: 1px solid #eaecef;
  margin: 1.4em 0;
}
img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 12px auto;
  border: 1px solid #e1e4e8;
  border-radius: 4px;
}
`.trim(),
  "utf8"
);

execSync(`npx --yes md-to-pdf body.md --dest out.pdf --stylesheet vscode-preview.css`, {
  stdio: "inherit",
  cwd: workDir,
  shell: true,
  env: process.env,
});

const outPdf = join(workDir, "out.pdf");
if (!existsSync(outPdf)) {
  console.error("Expected PDF not created:", outPdf);
  process.exit(1);
}
copyFileSync(outPdf, OUT);
console.log("Done:", OUT);
