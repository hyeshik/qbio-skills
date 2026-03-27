# Claude Code Skills

Custom skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Skills

### snu-procurement-doc

Automatically generates procurement specification and usage description documents for high-value research equipment purchases at Seoul National University. Given a manufacturer, model, and quantity, it researches specs and tariff codes via web search, then produces two HWPX (Hancom Office) documents ready for submission.

### snu-srnd

Browser automation skill for SRnD (서울대학교 연구행정통합관리시스템, srnd.snu.ac.kr). Controls the Nexacro Platform 14-based UI via `javascript_tool` to perform research administration tasks including project lookup, expenditure requests, researcher management, card billing, research achievements, procurement, and travel requests.

### snu-external-lecture-report

Automates filing external lecture/activity reports on the mySNU portal. Extracts activity details (type, organization, topic, date, compensation, etc.) from emails or official documents, fills in the mySNU external lecture report form via Chrome browser automation, and optionally generates a business trip request document (HWPX) with a Trello card for in-person activities.

### gmail-autoreply-drafter

Scans the Gmail inbox for unanswered emails, researches context from Sent mail and thread history, then composes and saves draft replies in the user's voice and style. Drafts are never sent — only saved for review. For each email, it generates multiple alternative versions (e.g., accept/decline/ask for details) separated by `--` dividers, so the user can pick the best option. Matches reply language to the incoming email and uses placeholders for anything requiring the user's confirmation.

### iris-assistant

Proactive assistant for the IRIS R&D 업무포털 (iris.go.kr), the Korean government's integrated R&D management system. Rather than simply directing users to pages, it navigates the Nexacro-based portal via Chrome browser automation and JavaScript API calls to perform tasks on behalf of the PI (연구책임자): project registration, agreement applications/changes, research fund management, achievement registration, report submission, settlement, technology fees, and payments. All significant actions are recorded in an audit trail HTML file for accountability.

### paper-interview

Generates a podcast-style in-depth scientific interview that introduces an academic paper. Uses a multi-agent pipeline (6 specialist analysts → editor → writer) to produce a rich, engaging dialogue between a science interviewer and the paper's author. The user drops a PDF; background context is gathered via web search and PubMed. The final output is a professionally typeset PDF compiled with Typst, complete with embedded Mermaid diagrams and figures extracted from the original paper. Supports English and Korean output.

### manuscript-review

Runs a multi-perspective review panel on an academic manuscript draft to help authors improve it for high-impact publication. Simulates 13 specialist reviewers — from hostile same-field experts to visionary mentors — who each review the paper, discuss disagreements, and produce a synthesized improvement roadmap. Agents actively search PubMed, bioRxiv, and the web for references and context. The output is an interactive HTML report with collapsible reviewer cards, Mermaid diagrams, and a prioritized action plan.

### auto-labnote

Summarizes the current Claude Code session into a structured scientific laboratory notebook entry and publishes it to a Notion database. Reads configuration (database URL, researcher name, language) from `.labnote-config.json`, then reviews the entire conversation history to compose a comprehensive lab note with sections for objective, methods, work performed, results, and next steps. Supports both English and Korean output, automatically detects whether to create a new page or update an existing one from the same day, and populates metadata from the git repository. Triggered by `/send-note` or natural-language requests like "send note" or "log this session".
