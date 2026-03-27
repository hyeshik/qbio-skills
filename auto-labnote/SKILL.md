---
name: send-note
description: "Write and post a comprehensive laboratory notebook entry to Notion, summarizing all work from the current Claude Code session. Use this skill on '/send-note' or when the user asks to create a lab note, post session notes, write up today's work, document the session in Notion, save to lab notebook, or send notes. Even casual requests like 'send note', 'lab note', 'post to notion', 'write up what we did', or 'log this session' should trigger this skill."
---

# Laboratory Notebook — Notion Publisher

Summarize the current Claude Code session into a structured scientific laboratory notebook entry and publish it to a Notion database.

## Step 1: Load Configuration

Read `.labnote-config.json` from the current working directory.

```json
{
  "database_url": "https://www.notion.so/...",
  "researcher": "Name",
  "language": "en"
}
```

The `language` field controls the language of the lab note body:
- `"en"` — English (default)
- `"ko"` — Korean (한국어)

**If the file is missing or unreadable**, ask the user:
1. The full URL of the Notion database where lab notes should go (e.g., `https://www.notion.so/xxxxx?v=yyyyy`).
2. Their name (suggest the output of `git config user.name` as default).
3. Preferred language: English or Korean.

**If the file exists but `language` is missing**, ask the user to choose between English and Korean before proceeding. Update the config file with the chosen language.

Write `.labnote-config.json` with these values and proceed.

## Step 2: Fetch Database Schema

Use the Notion `fetch` tool on the database URL from the config to retrieve:
- The database schema (property names and types)
- The data source ID (from `<data-source>` tags — you need this as the parent when creating pages)

Also fetch the Notion Markdown spec from `notion://docs/enhanced-markdown-spec` via `ReadMcpResourceTool` so you format page content correctly.

Identify the **title property** name from the schema (it may not be called "title" — use whatever the schema says). Also note any Date, Tags, Status, or other properties you can populate.

## Step 3: Determine Create vs Update

Decide whether to create a new page or update an existing one. Use a two-tier check:

### Tier 1: Conversation history (primary)

Check your own conversation history for a prior `/send-note` invocation that successfully created or updated a Notion page. If you find one, you already know the page ID and URL — this is an **update**.

This is the most reliable check because the conversation context *is* the session, even across `--resume`, host changes, or PID reuse.

### Tier 2: File fallback (for context compression)

If your conversation history has been compressed and you cannot find a prior `/send-note` result, fall back to `.labnote-session.json`:

```json
[
  {
    "date": "2026-03-27",
    "title": "2026-03-27 Created /send-note Skill ...",
    "page_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "page_url": "https://www.notion.so/..."
  }
]
```

The file is a flat list of recently created lab note pages. Check for entries matching today's date:
- **No entries today** → this is a **create** operation.
- **One or more entries today** → ask the user whether to update one of the listed pages or create a new one. Show the title of each candidate so the user can choose.

### Housekeeping

When writing back to the file, remove entries older than 7 days to prevent unbounded growth.

## Step 4: Compose the Lab Note

Review the **entire** conversation history of this session. Synthesize a comprehensive laboratory notebook entry. The goal is that someone reading this note months later can understand what was done, why, and what the results were.

### Language

Write the lab note body in the language specified by `language` in `.labnote-config.json`:
- **`"en"`**: Write entirely in English.
- **`"ko"`**: Write section headings and prose in Korean. Keep technical terms, code snippets, file paths, command-line output, variable/function names, and git commit messages in their original form (typically English). For example: "miR-21 mimic을 HeLa 세포에 transfection하여 cell viability 변화를 분석하였다" — mixing Korean prose with English technical terms naturally, as a Korean-speaking scientist would write.

### Title

Format: **`YYYY-MM-DD <Concise description of the primary work>`**

Examples:
- `2026-03-27 Analyzed miR-21 overexpression effects on HeLa cell viability`
- `2026-03-27 Fixed differential expression pipeline for miRNA transfection data`
- `2026-03-27 Benchmarked miR-155 knockdown efficiency across cell lines`

### Page Content Structure

Compose the body using **Notion-flavored Markdown** (fetched in Step 2). Do not repeat the title in the body — it goes in the properties.

Use these sections, adapting depth to session complexity. Skip sections that genuinely don't apply, but always include **Objective**, **Work Performed**, and **Results**.

```
## Metadata
- **Date**: YYYY-MM-DD
- **Researcher**: <name from config>
- **Working Directory**: `<absolute path>`
- **Repository**: `<git remote URL if available>`
- **Branch**: `<current git branch>`
- **Session Commits**: <list any commits made during this session, with short hashes and messages>

## Objective
<What was the goal of this session? 1-3 sentences, clear and direct.>

## Background
<Why this work was needed. Prior context, preceding sessions, or motivation.
Skip if the objective is self-explanatory.>

## Methods / Approach
<Strategy taken. Key design decisions and their rationale.
Tools, algorithms, or techniques used.>

## Work Performed
<Chronological account of what was done. Include:
- Files modified with brief descriptions of changes
- Commands run and their purposes
- Configuration changes
- Short, relevant code snippets in fenced code blocks
- Errors encountered and how they were resolved>

## Results
<Concrete outcomes with actual numbers:
- Test results: "12/12 qPCR samples passed quality control" not "all samples passed"
- Measurements: "miR-21 transfection reduced cell viability by 34.2% (p < 0.001)"
- Benchmarks with before/after comparisons
Format numerical data as tables when there are 3+ data points.>

## Figures and Artifacts
<List files generated during the session:
- Plots, images, reports (with full paths)
- Generated data files
- Build artifacts
If no files were generated, skip this section entirely.>

## Discussion
<Interpretation: what worked, what didn't, surprises, difficulties.
Skip for straightforward sessions with no notable observations.>

## Conclusions
<1-3 sentence summary of achievements and current state.>

## Next Steps
<What remains to be done. What the next session should focus on.
Bullet list preferred.>
```

### Content Guidelines

- **Include real data.** Actual numbers, actual error messages, actual file paths. A lab note's value is in its specificity.
- **Use fenced code blocks** (` ```language `) for commands, code snippets, and terminal output. Set the language tag when known.
- **Use Notion tables** (`<table>...</table>`) for structured numerical results — they render much better than markdown tables in Notion.
- **Use callouts** (`<callout icon="..." color="...">`) to highlight important warnings, key findings, or decisions.
- **Be comprehensive but not verbose.** Write like a scientist documenting for reproducibility, not like a chatbot summarizing a conversation.

## Step 5: Publish to Notion

### Creating a New Page

1. Use `notion-create-pages` with:
   - **parent**: `{ "data_source_id": "<id from Step 2>" }` (use `database_id` only if the database has a single data source; prefer `data_source_id` when available)
   - **pages**: array with one page object:
     - **properties**: set the title property (using the correct property name from schema) to the formatted title. Populate Date, Tags, or other properties if they exist in the schema.
     - **content**: the full lab note body in Notion Markdown
     - **icon**: `"🔬"`
2. Extract the page ID and URL from the response.
3. Update `.labnote-session.json` — read the existing file (or start with `[]`), append the new entry, prune entries older than 7 days, and write back:
   ```json
   [
     {
       "date": "YYYY-MM-DD",
       "title": "<the page title>",
       "page_id": "<page_id>",
       "page_url": "<url>"
     }
   ]
   ```

### Updating an Existing Page

1. First `fetch` the existing page (using the page_id from `.labnote-session.json`) to get its current content.
2. Use `notion-update-page` with:
   - **page_id**: from `.labnote-session.json`
   - **command**: `"replace_content"`
   - **new_str**: the updated full lab note body
   - Also update the title property if the scope of work changed, using **command**: `"update_properties"` (this requires a separate call).
3. Update the matching entry in `.labnote-session.json` (replace it in-place; prune entries older than 7 days).

When updating, mention at the top of the Discussion section that this note was updated with additional work from the same session.

## Step 6: Confirm to User

Display clearly:
- Whether a **new page was created** or an **existing page was updated**
- The **clickable URL** to the Notion page
- A **one-line summary** of what was documented

Example output:
```
Lab note created: 2026-03-27 Analyzed miR-21 overexpression effects on HeLa cell viability
https://www.notion.so/xxxxxxxx

Documented: objective, 3 modified scripts, qPCR validation, cell viability assay results.
```

## Notes

- `.labnote-session.json` is ephemeral session state. Recommend adding it to `.gitignore`.
- If Notion MCP tools are unavailable, tell the user to set up the Notion integration first (e.g., `/mcp` to authenticate).
- Gather git information (`git log`, `git remote -v`, `git branch`) to populate the Metadata section — run these commands as part of composing the note.
- When the session involved debugging, include the error messages and the fix in detail — these are the most valuable parts of a lab note.
