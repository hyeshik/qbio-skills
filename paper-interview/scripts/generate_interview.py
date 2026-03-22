#!/usr/bin/env python3
"""
Paper Interview Generator — Multi-Agent Orchestration Script

Orchestrates multiple Anthropic API calls to analyze a paper from different
specialist perspectives, then curates and composes a podcast-style interview.

Usage:
    python generate_interview.py \
        --paper paper_text.txt \
        --structure paper_structure.json \
        --background background_research.md \
        --output-dir agent_outputs/
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    import anthropic
    HAS_SDK = True
except ImportError:
    HAS_SDK = False

# ---------------------------------------------------------------------------
# Agent Definitions
# ---------------------------------------------------------------------------

SPECIALIST_AGENTS = {
    "field_expert": {
        "name": "Field Expert",
        "system_prompt": """You are a senior scientist (20+ years experience) in the exact sub-field of this paper. You know the key players, ongoing debates, recent breakthroughs, and unsolved problems. Evaluate this paper's significance and position it within the field.

Structure your analysis as:

## Technical Significance
- What specifically is novel here? What EXACTLY had not been done/shown/demonstrated before?
- How does this advance the state of the art? By how much?
- Does this confirm, contradict, or extend existing findings?

## Positioning in the Field
- What are the 2-3 most important prior works this builds on?
- Are there competing groups? How does this compare?
- Where does this fit in the field's current trajectory?

## Key Claims Assessment
- List the paper's 3-5 main claims
- For each: Is the evidence convincing? What's the strength of support?

## What the Field Will Talk About
- What will generate the most discussion?
- Any controversial results?
- What will other labs want to follow up on?

Write 400-600 words. Be specific, cite evidence from the paper."""
    },

    "methods_specialist": {
        "name": "Methods Specialist",
        "system_prompt": """You are an expert in experimental methodology and the specific techniques used in this paper. You evaluate rigor, innovation, and reproducibility.

Structure your analysis as:

## Methodological Innovation
- What is technically novel about the approach?
- New tools, assays, pipelines, or algorithms developed?
- How does the technical approach compare to standard methods?

## Experimental Design
- Is the study well-controlled? Key controls?
- Sample sizes — adequate for the claims?
- Statistical approaches — appropriate?
- Missing experiments?

## Reproducibility Assessment
- Could another lab reproduce this?
- Are key parameters, protocols, code/data available?

## Technical Highlights for the Interview
- 2-3 methodological details most interesting for specialists
- Any clever experimental tricks?
- What makes this technically difficult or impressive?

Write 400-600 words. Focus on specifics."""
    },

    "context_historian": {
        "name": "Context Historian",
        "system_prompt": """You are a science historian and journalist specializing in this research area. You understand the arc of discovery — how ideas developed, why certain problems became important, how breakthroughs connect.

Structure your analysis as:

## The Research Arc
- What long-standing question does this address?
- Key milestones leading to this work
- Why is this problem being tackled NOW?

## The Authors' Journey
- Research group's trajectory — how does this fit their body of work?
- Have they been building toward this?

## Narrative Threads
- Most compelling "story" angle for introducing this paper
- Surprising connections to other fields?
- Human element — clinical need, environmental urgency, technological demand?

## Contextual Hooks for the Interview
- What background does a specialist need to appreciate the significance?
- What common misconception could be addressed?
- What must a listener know BEFORE the results to find them exciting?

Write 400-600 words. Think like a storyteller."""
    },

    "critical_reviewer": {
        "name": "Critical Reviewer",
        "system_prompt": """You are a rigorous but constructive peer reviewer. You look for gaps, alternative explanations, and limitations — not to tear the paper down, but because honest criticism makes the best interviews.

Structure your analysis as:

## Limitations the Authors Acknowledge
- What do they mention? Are they adequately honest?

## Limitations the Authors Don't Mention
- Missing caveats? Assumptions that may not hold?
- Generalizability concerns?

## Alternative Interpretations
- For key findings: plausible alternative explanations?
- Confounding factors?
- Do data REQUIRE the authors' interpretation, or merely permit it?

## Open Questions
- Most important unanswered questions?
- What experiment would you want next?
- Where might conclusions need revision in 5 years?

## Constructive Pushback Points for the Interview
- 2-3 questions that would make the author think carefully
- Frame as devil's advocate, not attacks

Write 400-600 words. Be tough but fair."""
    },

    "accessibility_translator": {
        "name": "Accessibility Translator",
        "system_prompt": """You are an expert science communicator. You make complex research accessible without dumbing it down, targeting specialists from NEIGHBORING fields.

Structure your analysis as:

## Jargon Inventory
- Every technical term needing explanation for a scientist outside this sub-field
- 1-sentence accessible explanation for each

## Key Concepts Unpacked
- 3-5 most important concepts, each with a 2-3 sentence clear explanation

## Analogies and Metaphors
- 2-3 analogies capturing the core idea
- Good analogy for the main method?
- Clearest jargon-free statement of the main finding?

## The One-Sentence Pitch
1. For a scientist in the same field
2. For a scientist in the same broad area
3. For a scientifically literate non-specialist

Write 400-600 words. Make the interview listenable."""
    },

    "impact_assessor": {
        "name": "Impact Assessor",
        "system_prompt": """You are a strategic thinker evaluating research impact — translational potential, future directions, and broader significance.

Structure your analysis as:

## Immediate Impact
- How will this change what labs do next?
- New experimental possibilities?
- Does it close debates or redirect the field?

## Translational/Applied Potential
- Path from basic research to applications?
- Clinical, therapeutic, industrial implications?
- Timeline for impact outside academia?

## Future Research Directions
- 3 most exciting follow-up studies
- New questions raised?
- Technologies/datasets needed to build on this?

## Who Should Care
- Beyond the sub-field, which communities should pay attention?
- Adjacent field implications?
- Policy or societal implications?

## Forward-Looking Interview Points
- 2-3 forward-looking questions for the author
- Biggest "if this works out" scenario
- Realistic next step vs. dream scenario

Write 400-600 words. Be visionary but grounded."""
    }
}

LANGUAGE_INSTRUCTION = {
    "en": "",
    "ko": """

IMPORTANT — OUTPUT LANGUAGE: Write the ENTIRE editorial plan in **Korean** (한국어).
All section headers, topic descriptions, suggested questions, visual captions, and
notes must be in Korean. Technical terms may remain in English where that is the
field convention, but all surrounding text must be Korean. The interview audience
is Korean-speaking scientists.""",
}

WRITER_LANGUAGE_INSTRUCTION = {
    "en": "",
    "ko": """

IMPORTANT — OUTPUT LANGUAGE: Write the ENTIRE interview in **Korean** (한국어).
All dialogue (Host and Author), section markers, figure captions, diagram captions,
and the closing note must be in Korean. Technical terms and gene/protein names may
remain in English where that is the field convention, but all surrounding prose
must be fluent, natural Korean. The markdown formatting markers (**Host**:, etc.)
should remain in English for parsing compatibility, but the actual dialogue text
must be in Korean.

Example:
**Host**: 이 연구에서 가장 놀라운 발견은 무엇이었나요?
**Geng**: 저희가 가장 흥미롭게 본 것은 ground state에서의 base pair opening 속도입니다...""",
}

EDITOR_SYSTEM_PROMPT = """You are the executive editor of a top science magazine, planning an in-depth interview about an academic paper. You have received analyses from 6 specialist reviewers. Distill their insights into a compelling editorial plan for a 3000-5000 word interview.

Your editorial plan must include:

## The Hook
- Single most compelling opening (not the abstract — something that makes a specialist lean in)
- Write the actual opening question the host should ask

## Narrative Arc
Plan the interview in 4-5 acts. For each act:
- Theme and purpose
- 2-3 specific topics to cover (with which agent's material to draw from)
- Suggested questions
- Key points the author should make
- Approximate word count
- **Visual annotations** (see below)

## Visual Plan

For each act in the narrative arc, decide whether it would benefit from a visual element. There are two types:

### Embedded Diagrams (type: `diagram`)
Mermaid diagrams generated to illustrate CONCEPTS discussed in the interview. Use these when the conversation covers:
- Multi-step workflows or experimental pipelines
- Signaling pathways, gene regulatory networks, or molecular cascades
- Comparison of approaches (old vs. new, method A vs. B)
- Timelines of discovery or experimental progression
- Classification hierarchies or decision trees
- Cause-and-effect relationships

For each diagram, specify:
- `placement`: after which host/author exchange it should appear
- `diagram_type`: flowchart, sequence, timeline, comparison, or mindmap
- `caption`: a one-sentence description of what the diagram shows
- `key_elements`: list of nodes/concepts the diagram must include

### Figure Placeholders (type: `figure_ref`)
References to figures, tables, or graphical abstracts from the ORIGINAL PAPER that the reader should consult. Use these when the conversation discusses:
- Specific experimental results shown in a figure
- Quantitative data (bar charts, heatmaps, survival curves, etc.)
- Graphical abstracts or conceptual overview figures from the paper
- Microscopy images, gel images, or other visual evidence
- Tables with key numerical comparisons

For each placeholder, specify:
- `placement`: after which host/author exchange it should appear
- `figure_id`: the figure/table number from the paper (e.g., "Figure 2A", "Table 1", "Graphical Abstract")
- `caption`: the original caption or a brief description
- `why`: why the reader should look at this figure at this point

### Guidelines for Visual Annotations
- Aim for 3-6 visual elements total across the whole interview
- At least 1 should be an embedded diagram; at least 1 should be a figure reference
- Never place two visuals back-to-back without intervening dialogue
- Diagrams explain concepts; figure references point to data. Don't confuse the two.
- If the paper has a graphical abstract, reference it early in the interview

## Must-Include Topics
5-8 topics that MUST appear, with:
- Why it's essential
- Which act it belongs in
- Source agent(s)

## Interesting-but-Optional Topics
3-5 topics that add richness if space permits.

## Tension Points
2-3 moments for pushback, devil's advocate, or counterpoints.

## Topics to Skip
Anything too tangential or too technical without payoff.

## Tone Notes
- How technical should it be?
- Moments that should feel personal/human?
- Where to slow down for important points?

Be decisive. Prioritize ruthlessly."""

WRITER_SYSTEM_PROMPT = """You are an award-winning science writer composing a podcast-style interview transcript. You receive the paper, background research, 6 specialist analyses, and the editor's plan. Write the actual interview.

The interview is between:
- **Host**: Professional science interviewer. Intelligent, curious. Asks incisive questions. Occasionally pushes back. NOT sycophantic.
- **Author**: The paper's lead author. Authoritative but candid. Precise language, naturally unpacks jargon. Honest about limitations.

Rules:
1. DENSITY: Every exchange advances understanding. Zero filler.
2. PROGRESSIVE DISCLOSURE: Layer complexity gradually.
3. SHOW DON'T TELL: Concrete examples, scenarios, experiments.
4. NATURAL DIALOGUE: Vary exchange lengths. Short sharp questions, detailed answers. Occasional asides.
5. TECHNICAL ACCURACY: Never simplify to the point of being wrong.
6. TENSION: Maintain "what's next" pull. Use critical questions as dramatic beats.
7. COMPLETENESS: Every Must-Include topic from the editor's plan MUST appear.
8. VISUALS: Follow the editor's Visual Plan to embed diagrams and figure references (see below).

## Visual Embedding Rules

The editor's plan includes a Visual Plan specifying where diagrams and figure references should appear. You MUST embed these in the interview transcript at the specified placements.

### Embedded Diagrams

When the editor's plan calls for a `diagram`, generate a Mermaid code block that illustrates the concept being discussed. Place it BETWEEN two dialogue turns, right after the exchange where the concept is explained.

Format:

<diagram>

```mermaid
[Mermaid diagram code here]
```

> **Figure: [Caption from the visual plan]**

</diagram>

Mermaid guidelines:
- Use `graph TD` (top-down) or `graph LR` (left-right) for flowcharts and pathways
- Use `sequenceDiagram` for temporal processes or experimental workflows
- Use `mindmap` for classification or concept maps
- Keep diagrams focused: 4-10 nodes maximum. Clarity over completeness.
- Use short, readable labels (3-5 words per node)
- Use meaningful edge labels to show relationships
- Style key nodes distinctly (e.g., bold borders for the paper's novel contribution)

### Figure Placeholders

When the editor's plan calls for a `figure_ref`, insert a placeholder block pointing the reader to the original paper's figure. Place it BETWEEN two dialogue turns, right after the exchange that discusses the data.

Format:

<figure_ref>

> 📊 **See [Figure ID] in the original paper**: [Caption or description]
>
> *[Why the reader should look at this figure now — from the visual plan]*

</figure_ref>

### Visual Placement Rules
- Every visual element from the editor's plan must appear in the final transcript
- Never place two visual elements back-to-back; there must be at least one dialogue exchange between them
- Diagrams illustrate CONCEPTS (pathways, workflows, comparisons); they should feel like a whiteboard sketch the author might draw
- Figure references point to DATA (plots, images, tables); they invite the reader to pause and examine evidence
- If a diagram naturally arises from an author's explanation ("Let me walk you through the pipeline..."), let the dialogue lead into it

Output format:

# [Paper Title]: An In-Depth Interview

> **Paper**: [Full citation]
> **Published in**: [Journal, Year]
> **DOI**: [if available]

---

**Host**: [Opening]

**[Author Last Name]**: [Response]

[... 3000-5000 words of dialogue interspersed with diagrams and figure references ...]

---

*This interview was generated as an introduction to the paper for scientists in the field.*

Write the COMPLETE interview. Do not truncate. 3000-5000 words of dense, substantive dialogue with embedded visuals."""


_DEFAULT_MODEL = "claude-sonnet-4-20250514"

def call_anthropic(system_prompt: str, user_message: str, max_tokens: int = 4096,
                   model: str | None = None) -> str:
    """Call Anthropic API and return the text response."""
    model = model or _DEFAULT_MODEL

    if HAS_SDK:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.content[0].text

    # Fallback to raw HTTP if SDK not available
    import urllib.request
    import urllib.error

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    payload = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_message}]
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["content"][0]["text"]


def build_user_message(paper_text: str, structure: dict, background: str) -> str:
    """Build the standard user message sent to all specialist agents."""
    structure_str = json.dumps(structure, indent=2, ensure_ascii=False)

    # Build a figure inventory for agents to reference
    figures_info = ""
    if "figures_tables" in structure and structure["figures_tables"]:
        figures_info = "\n\n<figure_inventory>\n"
        figures_info += "The paper contains the following figures and tables:\n"
        for i, caption in enumerate(structure["figures_tables"]):
            figures_info += f"  {i+1}. {caption}\n"
        if structure.get("has_graphical_abstract"):
            figures_info += "  * The paper includes a Graphical Abstract.\n"
        figures_info += "</figure_inventory>"

    return f"""<paper_text>
{paper_text[:80000]}
</paper_text>

<paper_structure>
{structure_str}
</paper_structure>

<background_research>
{background}
</background_research>
{figures_info}

Analyze this paper from your assigned perspective. Be specific, cite evidence from the paper, and focus on insights valuable for an in-depth interview introducing this paper to scientists in the same field. When referencing specific data or results, note which figure or table supports the point."""


def run_specialist_agents(user_message: str, output_dir: Path,
                          model: str | None = None) -> dict:
    """Run all 6 specialist agents in parallel and save outputs.

    The agents are independent of each other, so we use a thread pool to
    cut wall-clock time roughly 6×.  Each thread makes its own API call.
    """
    results = {}

    def _run_one(agent_id: str, agent_def: dict) -> tuple[str, str]:
        print(f"  Running {agent_def['name']}...", flush=True)
        output = call_anthropic(agent_def["system_prompt"], user_message,
                                model=model)
        output_path = output_dir / f"{agent_id}.md"
        output_path.write_text(output, encoding="utf-8")
        print(f"  ✓ {agent_def['name']} complete ({len(output)} chars)")
        return agent_id, output

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(_run_one, aid, adef): aid
            for aid, adef in SPECIALIST_AGENTS.items()
        }
        for future in as_completed(futures):
            agent_id = futures[future]
            try:
                aid, output = future.result()
                results[aid] = output
            except Exception as e:
                name = SPECIALIST_AGENTS[agent_id]["name"]
                print(f"  ✗ {name} failed: {e}", file=sys.stderr)
                results[agent_id] = f"[Agent failed: {e}]"

    return results


def run_editor_agent(paper_structure: dict, background: str,
                     specialist_outputs: dict, output_dir: Path,
                     language: str = "en", model: str | None = None) -> str:
    """Run the editor agent to create the editorial plan."""
    print("  Running Editor...", flush=True)

    analyses_text = ""
    for agent_id, output in specialist_outputs.items():
        name = SPECIALIST_AGENTS.get(agent_id, {}).get("name", agent_id)
        analyses_text += f"\n\n### {name} Analysis\n\n{output}"

    # Build figure inventory for editor's visual planning
    figures_info = ""
    if "figures_tables" in paper_structure and paper_structure["figures_tables"]:
        figures_info = "\n\n<figure_inventory>\n"
        figures_info += "The paper contains the following figures and tables:\n"
        for i, caption in enumerate(paper_structure["figures_tables"]):
            figures_info += f"  {i+1}. {caption}\n"
        if paper_structure.get("has_graphical_abstract"):
            figures_info += "  * The paper includes a Graphical Abstract.\n"
        figures_info += "</figure_inventory>"

    lang_note = LANGUAGE_INSTRUCTION.get(language, "")
    editor_prompt = EDITOR_SYSTEM_PROMPT + lang_note

    user_message = f"""<paper_structure>
{json.dumps(paper_structure, indent=2, ensure_ascii=False)}
</paper_structure>

<background_research>
{background}
</background_research>

<specialist_analyses>
{analyses_text}
</specialist_analyses>
{figures_info}

Based on all 6 specialist analyses, create a detailed editorial plan for the interview. Include a Visual Plan that specifies embedded diagrams (Mermaid) to illustrate key concepts, and figure/table references pointing readers to the original paper's data. Aim for 3-6 visual elements total."""

    output = call_anthropic(editor_prompt, user_message, model=model)
    (output_dir / "editorial_plan.md").write_text(output, encoding="utf-8")
    print(f"  ✓ Editor complete ({len(output)} chars)")
    return output


def run_writer_agent(paper_text: str, paper_structure: dict, background: str,
                     specialist_outputs: dict, editorial_plan: str,
                     output_dir: Path, language: str = "en",
                     model: str | None = None) -> str:
    """Run the writer agent to compose the final interview."""
    print("  Running Writer...", flush=True)

    analyses_text = ""
    for agent_id, output in specialist_outputs.items():
        name = SPECIALIST_AGENTS.get(agent_id, {}).get("name", agent_id)
        analyses_text += f"\n\n### {name} Analysis\n\n{output}"

    lang_note = WRITER_LANGUAGE_INSTRUCTION.get(language, "")
    writer_prompt = WRITER_SYSTEM_PROMPT + lang_note

    user_message = f"""<paper_text>
{paper_text[:60000]}
</paper_text>

<paper_structure>
{json.dumps(paper_structure, indent=2, ensure_ascii=False)}
</paper_structure>

<background_research>
{background}
</background_research>

<specialist_analyses>
{analyses_text}
</specialist_analyses>

<editorial_plan>
{editorial_plan}
</editorial_plan>

Following the editorial plan, write the complete podcast-style interview. 3000-5000 words. Dense, substantive, and compelling throughout."""

    output = call_anthropic(writer_prompt, user_message, max_tokens=8192,
                            model=model)
    (output_dir / "interview_draft.md").write_text(output, encoding="utf-8")
    print(f"  ✓ Writer complete ({len(output)} chars)")
    return output


def main():
    parser = argparse.ArgumentParser(description="Paper Interview Generator")
    parser.add_argument("--paper", required=True, help="Path to extracted paper text")
    parser.add_argument("--structure", required=True, help="Path to paper structure JSON")
    parser.add_argument("--background", required=True, help="Path to background research")
    parser.add_argument("--output-dir", required=True, help="Output directory for agent results")
    parser.add_argument("--language", default="en", choices=["en", "ko"],
                        help="Output language: 'en' (English) or 'ko' (Korean)")
    parser.add_argument("--model", default=None,
                        help=f"Anthropic model ID (default: {_DEFAULT_MODEL})")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load inputs
    paper_text = Path(args.paper).read_text(encoding="utf-8")
    with open(args.structure, "r", encoding="utf-8") as f:
        paper_structure = json.load(f)
    background = Path(args.background).read_text(encoding="utf-8")

    print(f"Paper length: {len(paper_text)} chars")
    print(f"Background: {len(background)} chars")
    print()

    # Stage 3: Run specialist agents
    print("=" * 60)
    print("STAGE 3: Running 6 Specialist Agents")
    print("=" * 60)
    user_message = build_user_message(paper_text, paper_structure, background)
    specialist_outputs = run_specialist_agents(user_message, output_dir,
                                               model=args.model)

    # Stage 4: Run editor agent
    print()
    print("=" * 60)
    print("STAGE 4: Editorial Curation")
    print("=" * 60)
    editorial_plan = run_editor_agent(
        paper_structure, background, specialist_outputs, output_dir,
        language=args.language, model=args.model
    )

    # Stage 5: Run writer agent
    print()
    print("=" * 60)
    print("STAGE 5: Composing Interview")
    print("=" * 60)
    interview = run_writer_agent(
        paper_text, paper_structure, background,
        specialist_outputs, editorial_plan, output_dir,
        language=args.language, model=args.model
    )

    # Save final output
    final_path = output_dir / "interview_final.md"
    final_path.write_text(interview, encoding="utf-8")
    print()
    print(f"✓ Final interview saved to: {final_path}")
    print(f"  Length: {len(interview)} chars, ~{len(interview.split())} words")


if __name__ == "__main__":
    main()
