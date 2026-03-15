# Claude Code Skills

Custom skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Skills

### snu-procurement-doc

Automatically generates procurement specification and usage description documents for high-value research equipment purchases at Seoul National University. Given a manufacturer, model, and quantity, it researches specs and tariff codes via web search, then produces two HWPX (Hancom Office) documents ready for submission.

### snu-srnd

Browser automation skill for SRnD (서울대학교 연구행정통합관리시스템, srnd.snu.ac.kr). Controls the Nexacro Platform 14-based UI via `javascript_tool` to perform research administration tasks including project lookup, expenditure requests, researcher management, card billing, research achievements, procurement, and travel requests.
