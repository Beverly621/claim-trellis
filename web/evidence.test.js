const assert = require("node:assert/strict");
const { createHash } = require("node:crypto");
const { test } = require("node:test");
const { build, render } = require("./evidence.js");

const claim = "ChatGPT Advanced Data Analysis autonomously developed machine-learning models using clinical study data.";
const text = `After summarizing each clinical trial, researchers reviewed the workflow.\n\nFig. 1 | Study design. The tool autonomously selected the appropriate machine-learning models for the analysis following prompting. The researchers subsequently checked the results.\n\nMetastatic disease outcomes were reported separately.`;
const digest = (value) => createHash("sha256").update(value).digest("hex");
const passage = {
  text,
  start_char: 6323,
  end_char: 6323 + text.length,
  locator: `chars:6323-${6323 + text.length}`,
  sha256: digest(text),
};

test("long evidence exposes a verbatim, relevant primary sentence", () => {
  const view = build(claim, passage, { title: "paper.pdf" });
  assert.equal(
    view.primary,
    "The tool autonomously selected the appropriate machine-learning models for the analysis following prompting.",
  );
  assert.ok(text.includes(view.primary));
  assert.equal(view.location, "Figure 1 caption");
});

test("supporting blocks retain the entire canonical context in source order", () => {
  const view = build(claim, passage);
  assert.ok(view.supporting.length >= 3);
  assert.equal(view.supporting.map((block) => block.text).join(""), text);
  assert.equal(view.supporting[0].start, 0);
  assert.equal(view.supporting.at(-1).end, text.length);
});

test("projection is deterministic and never mutates hashes or provider input", () => {
  const before = structuredClone(passage);
  const providerInput = passage.text;
  assert.deepEqual(build(claim, passage), build(claim, passage));
  assert.deepEqual(passage, before);
  assert.equal(passage.sha256, digest(text));
  assert.equal(passage.text, providerInput);
});

test("locator shows real offsets, source and scope but no invented page", () => {
  const html = render(claim, passage, { title: "paper.pdf", access_tier: "full_text" });
  assert.match(html, /<dt>Characters<\/dt><dd>6323–/);
  assert.match(html, /<dt>Source<\/dt><dd>paper\.pdf<\/dd>/);
  assert.match(html, /<dt>Scope<\/dt><dd>full text<\/dd>/);
  assert.doesNotMatch(html, /<dt>Page<\/dt>/);
  assert.match(html, /Figure 1 caption/);
});

test("a real page value is shown only when present", () => {
  assert.match(render(claim, { ...passage, page: 2 }, {}), /<dt>Page<\/dt><dd>2<\/dd>/);
});

test("legacy passages with only text and offsets still render", () => {
  const html = render(claim, { text, start_char: 10, end_char: 10 + text.length }, {});
  assert.match(html, /Primary passage/);
  assert.match(html, /<dt>Characters<\/dt><dd>10–/);
  assert.doesNotMatch(html, /<dt>Page<\/dt>/);
});

test("native disclosure starts closed and exposes keyboard-accessible summary", () => {
  const html = render(claim, passage, {});
  assert.match(html, /<details class="supporting-context">\s*<summary>/);
  assert.doesNotMatch(html, /<details class="supporting-context" open/);
  assert.match(html, /Show context/);
  assert.match(html, /<h5 id="primary-passage-title"/);
});

test("uncertain segmentation falls back to the complete verbatim passage", () => {
  const source = "No safe sentence boundary here\nand another line with data-\nset unchanged";
  const view = build("unrelated claim", { text: source });
  assert.equal(view.primary, source);
  assert.equal(view.supporting.map((block) => block.text).join(""), source);
});

test("source text is escaped without creating synthetic evidence", () => {
  const source = "The <script> tag was studied. An unrelated result followed.";
  const html = render("script tag", { text: source }, {});
  assert.match(html, /&lt;script&gt;/);
  assert.doesNotMatch(html, /<script>/);
});

test("single long paragraphs split into readable blocks without dropping text", () => {
  const source = Array.from({ length: 20 }, (_, index) =>
    `Sentence ${index} documents a distinct clinical result and its surrounding context.`,
  ).join(" ");
  const view = build("clinical result", { text: source });
  assert.ok(view.supporting.length > 1);
  assert.equal(view.supporting.map((block) => block.text).join(""), source);
});
