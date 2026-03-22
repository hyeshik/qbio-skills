# Running the Review via the Orchestrator Script

This is the automated pipeline approach. It requires an Anthropic API key
and calls Claude's API once per reviewer persona. If the API is unavailable
or you prefer more control, use Manual Orchestration in the main SKILL.md.

## Prerequisites

```bash
pip install anthropic pdfplumber python-docx markdown --break-system-packages -q
```

The `markdown` library is used by the HTML report formatter. All other
dependencies are optional and used for manuscript extraction.

## Step 1: Prepare the manuscript

Check what the user uploaded. Supported formats: PDF, DOCX, Markdown, plain text.

For PDFs, do a quick extraction test to make sure text comes through cleanly:
```bash
pdftotext -f 1 -l 1 <manuscript.pdf> - | head -30
```

If extraction looks garbled (common with two-column layouts or embedded
fonts), the script falls back to pdfplumber or pymupdf automatically.

## Step 2: Run the panel

```bash
python <skill-path>/scripts/review_panel.py \
    <manuscript_file> \
    --output <output_dir>/
```

The script will:
- Extract text from the manuscript
- Run each agent sequentially (each makes an API call with web search
  where appropriate)
- Identify disagreements among reviews
- Run a moderated discussion
- Synthesize the final report
- Save an HTML report (primary) and Markdown report (supplementary)
  to the output directory

### Running a subset of agents

```bash
python review_panel.py manuscript.pdf --agents devils_advocate professional_editor trend_expert
```

### Adding context (cover letter, target journal, etc.)

```bash
python review_panel.py manuscript.pdf --context cover_letter.txt
```

## Step 3: Present the report

Copy the HTML report to the user's output directory and present it using
`present_files`. Walk the user through the executive summary and top
priorities conversationally.

## Error Handling

- If the Anthropic API key is not set, fall back to manual orchestration.
- If PDF extraction produces garbled text, try pdfplumber, pymupdf, or
  rasterize-and-OCR.
- If a single agent fails, the script logs the error and continues.
  The synthesis can work with incomplete reviews.
- If the manuscript is very long (>50 pages), consider reviewing sections
  separately or truncating supplementary material.
