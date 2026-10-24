const fs = require("node:fs");
const path = require("node:path");
const {
  AlignmentType,
  BorderStyle,
  Document,
  Footer,
  HeadingLevel,
  LevelFormat,
  NumberFormat,
  PageBreak,
  PageNumber,
  Packer,
  Paragraph,
  SectionType,
  ShadingType,
  SimpleField,
  Table,
  TableCell,
  TableOfContents,
  TableRow,
  TextRun,
  VerticalAlign,
  WidthType,
} = require("C:/Users/dangv/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/docx");

const workspace = path.resolve(__dirname, "..");
const markdownPath = path.join(workspace, "deliverables", "FPT_Internship_Report_Content_Revised.md");
const outputPath = path.join(workspace, "deliverables", "Bao_Cao_Thuc_Tap_Tot_Nghiep_FPT_YOLO.docx");
const source = fs.readFileSync(markdownPath, "utf8").replace(/\r\n/g, "\n");
const lines = source.split("\n");
const front = [];
const body = [];
let blocks = front;
let inBody = false;
let coverMode = 0;
let skipFrontLines = false;
let currentHeading = "";
let tableNumber = 0;
let currentPart = 0;
const tableCountsByPart = { 1: 0, 2: 0, 3: 0 };
let titleSeen = 0;

const pageWidth = 11906;
const contentWidth = 9070;
const border = { style: BorderStyle.SINGLE, size: 1, color: "A6A6A6" };
const tableBorders = { top: border, bottom: border, left: border, right: border, insideH: border, insideV: border };

function textRuns(text, forceBold = false, size = 26) {
  const runs = [];
  const pattern = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[[^\]]+\]\([^)]+\))/g;
  let last = 0;
  for (const match of text.matchAll(pattern)) {
    if (match.index > last) runs.push(new TextRun({ text: text.slice(last, match.index), bold: forceBold, size }));
    const token = match[0];
    if (token.startsWith("**")) runs.push(new TextRun({ text: token.slice(2, -2), bold: true, size }));
    else if (token.startsWith("*")) runs.push(new TextRun({ text: token.slice(1, -1), italics: true, bold: forceBold, size }));
    else if (token.startsWith("`")) runs.push(new TextRun({ text: token.slice(1, -1), font: "Consolas", size: 22, bold: forceBold }));
    else {
      const link = token.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
      runs.push(new TextRun({ text: `${link[1]} (${link[2]})`, bold: forceBold, size }));
    }
    last = match.index + token.length;
  }
  if (last < text.length) runs.push(new TextRun({ text: text.slice(last), bold: forceBold, size }));
  return runs.length ? runs : [new TextRun({ text, bold: forceBold, size })];
}

function addParagraph(target, text, options = {}) {
  const { style, cover, title, caption, captionIndex, captionPart, numberedText, bullet, leftAlign, centeredSection } = options;
  if (cover && !text.trim()) return;
  const topicTitle = cover && /^\*\*(ĐỀ TÀI|Nội dung thực tập|Chuyên đề):/.test(text);
  const isHeading = /^Heading[1-4]$/.test(style || "");
  const isSectionTitle = style === "Title" || style === "ReportIntroTitle" || centeredSection;
  const headingLevel = { Heading1: HeadingLevel.HEADING_1, Heading2: HeadingLevel.HEADING_2, Heading3: HeadingLevel.HEADING_3, Heading4: HeadingLevel.HEADING_4 }[style];
  const paragraphStyle = style || (cover ? undefined : bullet ? "ListBody" : numberedText && leftAlign ? "Normal" : "DoanVB");
  let children = textRuns(text, topicTitle || isHeading || isSectionTitle, cover ? (topicTitle ? 36 : 28) : isSectionTitle ? 28 : 26);
  if (caption) {
    const sequenceField = captionIndex === 1 ? `SEQ Bảng \\r 1 \\* ARABIC` : `SEQ Bảng \\* ARABIC`;
    children = [new TextRun({ text: `Bảng `, font: "Times New Roman", size: 26, italics: true }), new TextRun({ text: `${captionPart}.`, font: "Times New Roman", size: 26, italics: true }), new SimpleField(sequenceField, String(captionIndex)), new TextRun({ text: `. ${caption}`, font: "Times New Roman", size: 26, italics: true })];
  }
  if (numberedText) children = textRuns(numberedText);
  const alignment = cover || isSectionTitle ? AlignmentType.CENTER : caption ? AlignmentType.CENTER : leftAlign ? AlignmentType.LEFT : isHeading ? AlignmentType.LEFT : AlignmentType.JUSTIFIED;
  target.push(new Paragraph({
    ...(headingLevel ? { heading: headingLevel } : paragraphStyle ? { style: paragraphStyle } : {}),
    alignment,
    keepNext: Boolean(title || caption),
    indent: cover || caption || isSectionTitle || isHeading || leftAlign || bullet ? undefined : { firstLine: 567 },
    ...(cover ? { spacing: { before: title ? 120 : 0, after: 120, line: 312 } } : caption ? {} : centeredSection ? { spacing: { before: 0, after: 360, line: 312 } } : isHeading || isSectionTitle ? {} : { spacing: { before: 0, after: 120, line: 312 } }),
    children: cover && title ? [new TextRun({ text, font: "Times New Roman", size: 60, bold: true })] : children,
    ...(bullet ? { numbering: { reference: "report-bullets", level: 0 } } : {}),
  }));
}

function addTable(target, tableLines) {
  const rows = tableLines.map((line) => line.split("|").slice(1, -1).map((cell) => cell.trim()));
  const useful = rows.filter((row) => row.length && !row.every((cell) => /^:?-{2,}:?$/.test(cell)));
  if (!useful.length) return;
  tableNumber += 1;
  const headers = useful[0];
  const captionHeading = currentHeading.replace(/^\d+(?:\.\d+)*\.?\s+/, "");
  const caption = `${captionHeading}${headers[0] ? ` - ${headers[0]}` : ""}`.slice(0, 110);
  if (currentPart > 0) {
    tableCountsByPart[currentPart] += 1;
    addParagraph(target, "", { caption, captionPart: currentPart, captionIndex: tableCountsByPart[currentPart] });
  }
  const colCount = Math.max(1, ...useful.map((row) => row.length));
  const base = Math.floor(contentWidth / colCount);
  const widths = Array.from({ length: colCount }, (_, i) => i === colCount - 1 ? contentWidth - base * (colCount - 1) : base);
  const wordRows = useful.map((row, rowIndex) => new TableRow({
    tableHeader: rowIndex === 0,
    cantSplit: true,
    children: widths.map((width, columnIndex) => {
      const cellText = row[columnIndex] || "";
      const isNumeric = /^-?\d+(?:[.,]\d+)?$/.test(cellText.trim());
      return new TableCell({
        width: { size: width, type: WidthType.DXA },
        borders: tableBorders,
        margins: { top: 70, bottom: 70, left: 90, right: 90 },
        verticalAlign: VerticalAlign.CENTER,
        ...(rowIndex === 0 ? { shading: { fill: "DCE6F1", type: ShadingType.CLEAR } } : {}),
        children: [new Paragraph({
          alignment: rowIndex === 0 ? AlignmentType.CENTER : isNumeric ? AlignmentType.RIGHT : AlignmentType.LEFT,
          spacing: { before: 120, after: 120, line: 288 },
          children: textRuns(cellText, rowIndex === 0, 26),
        })],
      });
    }),
  }));
  target.push(new Table({
    width: { size: contentWidth, type: WidthType.DXA },
    columnWidths: widths,
    rows: wordRows,
  }));
  target.push(new Paragraph({ spacing: { after: 120 }, children: [new TextRun("")] }));
}

function isSeparator(line) {
  return /^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?\s*$/.test(line);
}

function addHeading(target, level, text, inCover) {
  currentHeading = text;
  const partMatch = text.match(/^PHẦN (I|II|III)\./);
  if (partMatch) currentPart = { I: 1, II: 2, III: 3 }[partMatch[1]];
  if (text === "BÌA") { coverMode = 1; return; }
  if (text === "BÌA PHỤ") { target.push(new Paragraph({ children: [new PageBreak()] })); coverMode = 2; return; }
  if (text === "LỜI CẢM ƠN") {
    target.push(new Paragraph({ children: [new PageBreak()] })); coverMode = 0;
    addParagraph(target, text, { style: "Title", title: true }); return;
  }
  if (text === "MỤC LỤC") {
    target.push(new Paragraph({ children: [new PageBreak()] })); coverMode = 0;
    addParagraph(target, text, { style: "Title", title: true });
    target.push(new Paragraph({ style: "TOCPageHeader", alignment: AlignmentType.RIGHT, spacing: { before: 0, after: 120 }, children: [new TextRun({ text: "Trang", font: "Times New Roman", size: 26 })] }));
     target.push(new Paragraph({ style: "TOCManual", alignment: AlignmentType.LEFT, spacing: { before: 100, after: 120 }, children: [new TextRun({ text: "LỜI MỞ ĐẦU", bold: true, size: 28 })] }));
    target.push(new TableOfContents("Mục lục", { hyperlink: true, headingStyleRange: "1-3", beginDirty: true }));
    skipFrontLines = true; return;
  }
   if (text === "DANH MỤC CÁC BẢNG BIỂU, HÌNH VẼ, ĐỒ THỊ, CÔNG THỨC") {
    target.push(new Paragraph({ children: [new PageBreak()] }));
    addParagraph(target, text, { style: "Title", title: true });
    target.push(new Paragraph({ style: "TOCPageHeader", alignment: AlignmentType.RIGHT, spacing: { before: 0, after: 120 }, children: [new TextRun({ text: "Trang", font: "Times New Roman", size: 26 })] }));
     target.push(new TableOfContents("Danh mục bảng", { captionLabelIncludingNumbers: "Bảng", hyperlink: true, beginDirty: true }));
    skipFrontLines = true; return;
  }
   if (text === "DANH MỤC VIẾT TẮT") {
    target.push(new Paragraph({ children: [new PageBreak()] }));
    addParagraph(target, text, { style: "Title", title: true }); return;
  }
  if (text === "LỜI MỞ ĐẦU") {
    target.push(new Paragraph({ children: [new PageBreak()] }));
    addParagraph(target, text, { style: "ReportIntroTitle", title: true }); return;
  }
  if (!inBody && text.startsWith("PHẦN I.")) {
    inBody = true; blocks = body; target = body;
    currentHeading = text;
    addParagraph(target, text, { style: "Heading1", title: true }); return;
  }
  const isMajor = level === 1;
  const isChapter = level === 2 && text.startsWith("CHƯƠNG ");
  if ((isMajor && inBody && !text.startsWith("PHẦN I.")) || isChapter) target.push(new Paragraph({ children: [new PageBreak()] }));
  currentHeading = text;
  let style;
  if (isMajor) style = "Heading1";
  else if (isChapter || level === 2) style = "Heading2";
  else if (level === 3) style = "Heading3";
  else style = "Heading4";
  const centeredSection = text === "KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN" || text === "TÀI LIỆU THAM KHẢO";
  addParagraph(target, text, { style, title: true, centeredSection });
}

for (let i = 0; i < lines.length;) {
  const line = lines[i];
  if (skipFrontLines) {
    if (line.trim() === "---") skipFrontLines = false;
    i += 1; continue;
  }
  if (!line.trim() || line.trim() === "---" || line.trim().startsWith(">")) { i += 1; continue; }
  const target = inBody ? body : front;
  const heading = line.match(/^(#{1,6})\s+(.+)$/);
  if (heading) {
    const text = heading[2].trim();
    if (!inBody && titleSeen < 2 && (text === "BÁO CÁO THỰC TẬP TỐT NGHIỆP" || text.startsWith("Gán nhãn dữ liệu và tinh chỉnh"))) { titleSeen += 1; i += 1; continue; }
    if (text.startsWith("BÁO CÁO THỰC TẬP") && coverMode) { addParagraph(target, text, { cover: true, title: true }); i += 1; continue; }
    addHeading(target, heading[1].length, text, Boolean(coverMode));
    i += 1; continue;
  }
  if (line.trim().startsWith("|")) {
    const tableLines = [];
    while (i < lines.length && lines[i].trim().startsWith("|")) {
      if (!isSeparator(lines[i])) tableLines.push(lines[i]);
      i += 1;
    }
    addTable(target, tableLines);
    continue;
  }
  if (line.trim().startsWith("- ")) {
    addParagraph(target, line.trim().slice(2), { bullet: true });
    i += 1; continue;
  }
  if (/^\s*\d+\.\s+/.test(line)) {
    addParagraph(target, "", { numberedText: line.trim(), leftAlign: currentHeading === "TÀI LIỆU THAM KHẢO" });
    i += 1; continue;
  }
  const paragraphLines = [line.trim()];
  i += 1;
  while (i < lines.length && lines[i].trim() && !/^(#{1,6})\s+/.test(lines[i]) && !lines[i].trim().startsWith("|") && !lines[i].trim().startsWith("- ") && !/^\s*\d+\.\s+/.test(lines[i]) && lines[i].trim() !== "---" && !lines[i].trim().startsWith(">")) {
    paragraphLines.push(lines[i].trim());
    i += 1;
  }
  const paragraph = paragraphLines.join(" ");
  const isCover = Boolean(coverMode);
  addParagraph(target, paragraph, { cover: isCover });
}

const footer = new Footer({
  children: [new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ children: [PageNumber.CURRENT], font: "Times New Roman", size: 26 })],
  })],
});

const doc = new Document({
  numbering: {
    config: [{
      reference: "report-bullets",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 850, hanging: 283 } } } }],
    }],
  },
  styles: {
    default: { document: { run: { font: "Times New Roman", size: 26 } } },
    paragraphStyles: [
      { id: "Normal", name: "Normal", run: { font: "Times New Roman", size: 26 }, paragraph: { alignment: AlignmentType.JUSTIFIED, spacing: { before: 120, after: 120, line: 312 }, indent: { left: 0, right: 0 } } },
      { id: "DoanVB", name: "DoanVB", basedOn: "Normal", next: "Normal", run: { font: "Times New Roman", size: 26 }, paragraph: { alignment: AlignmentType.JUSTIFIED, spacing: { before: 120, after: 120, line: 312 }, indent: { firstLine: 567 } } },
      { id: "ListBody", name: "List Body", basedOn: "Normal", next: "Normal", run: { font: "Times New Roman", size: 26 }, paragraph: { alignment: AlignmentType.JUSTIFIED, spacing: { before: 0, after: 120, line: 312 }, indent: { left: 0, right: 0 } } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Times New Roman", size: 26, bold: true }, paragraph: { alignment: AlignmentType.LEFT, spacing: { before: 0, after: 240, line: 312 }, indent: { left: 0, right: 0 }, outlineLevel: 0, keepNext: true } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Times New Roman", size: 26, bold: true }, paragraph: { alignment: AlignmentType.LEFT, spacing: { before: 120, after: 120, line: 312 }, indent: { left: 0, right: 0 }, outlineLevel: 1, keepNext: true } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Times New Roman", size: 26, bold: true, italics: true }, paragraph: { alignment: AlignmentType.LEFT, spacing: { before: 120, after: 120, line: 312 }, indent: { left: 0, right: 0 }, outlineLevel: 2, keepNext: true } },
      { id: "Heading4", name: "Heading 4", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Times New Roman", size: 26, bold: true, italics: true }, paragraph: { alignment: AlignmentType.LEFT, spacing: { before: 120, after: 120, line: 312 }, indent: { left: 0, right: 0 }, outlineLevel: 3, keepNext: true } },
      { id: "Title", name: "Title", basedOn: "Normal", next: "Normal", run: { font: "Times New Roman", size: 28, bold: true }, paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 0, after: 360, line: 312 }, indent: { left: 0, right: 0 }, keepNext: true } },
      { id: "ReportIntroTitle", name: "Report Intro Title", basedOn: "Normal", next: "Normal", run: { font: "Times New Roman", size: 28, bold: true }, paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 0, after: 360, line: 312 }, indent: { left: 0, right: 0 }, keepNext: true } },
      { id: "Caption", name: "Caption", basedOn: "Normal", next: "Normal", run: { font: "Times New Roman", size: 26, italics: true }, paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 120, after: 120, line: 312 }, indent: { left: 0, right: 0 }, keepNext: true } },
      { id: "TOC1", name: "TOC 1", basedOn: "Normal", run: { font: "Times New Roman", size: 28, bold: true, allCaps: true }, paragraph: { alignment: AlignmentType.LEFT, spacing: { before: 120, after: 120, line: 312 }, indent: { left: 0, right: 0 } } },
      { id: "TOC2", name: "TOC 2", basedOn: "Normal", run: { font: "Times New Roman", size: 26, bold: true }, paragraph: { alignment: AlignmentType.LEFT, spacing: { before: 120, after: 120, line: 312 }, indent: { left: 850, hanging: 567 } } },
      { id: "TOC3", name: "TOC 3", basedOn: "Normal", run: { font: "Times New Roman", size: 26, bold: true, italics: true }, paragraph: { alignment: AlignmentType.LEFT, spacing: { before: 120, after: 120, line: 312 }, indent: { left: 1276, hanging: 709 } } },
      { id: "TOCManual", name: "TOC Manual Entry", basedOn: "Normal", next: "Normal", run: { font: "Times New Roman", size: 28, bold: true }, paragraph: { alignment: AlignmentType.LEFT, spacing: { before: 120, after: 120, line: 312 }, indent: { left: 0, right: 0 } } },
      { id: "TOCPageHeader", name: "TOC Page Header", basedOn: "Normal", next: "Normal", run: { font: "Times New Roman", size: 26 }, paragraph: { alignment: AlignmentType.RIGHT, spacing: { before: 0, after: 120, line: 312 }, indent: { left: 0, right: 0 } } },
    ],
  },
  sections: [
    {
      properties: { page: { size: { width: pageWidth, height: 16838 }, margin: { top: 1134, right: 1134, bottom: 1134, left: 1701, header: 567, footer: 567 } } },
      children: front,
    },
    {
      properties: { type: SectionType.NEXT_PAGE, page: { size: { width: pageWidth, height: 16838 }, margin: { top: 1134, right: 1134, bottom: 1134, left: 1701, header: 567, footer: 567 }, pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL } } },
      footers: { default: footer },
      children: body,
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(outputPath, buffer);
  console.log(`Created ${outputPath} (${buffer.length} bytes; ${tableNumber} tables).`);
}).catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
