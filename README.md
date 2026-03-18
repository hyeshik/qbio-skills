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
