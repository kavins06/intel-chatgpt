# intel

![intel logo](assets/intel-logo.jpg)

**Research deeply. Challenge assumptions. Decide clearly.**

intel is an open-source intelligence plugin that helps an AI agent investigate complex questions and turn evidence into practical decisions. It combines ten skills for research, diagnosis, competitive strategy, stakeholder analysis, foresight, innovation, risk, critical review, and clear communication.

Start with a question, a decision, or a set of documents. The coordinator selects the relevant skills, guides the investigation, and brings the findings together.

[How it works](#how-it-works) · [Skills](#the-ten-skills) · [Examples](#try-it) · [Installation](#install-from-github)

## How it works

For deep work, intel follows four passes:

| Pass | What happens | What it produces |
|---|---|---|
| **Frame** | Define the decision, scope, alternatives, and questions that matter. Establish initial hypotheses and what could change them. | A focused question and investigation plan. |
| **Investigate** | Gather evidence, inspect sources, check definitions and calculations, and look for conflicting accounts. | Supported findings, traceable claims, and explicit information gaps. |
| **Challenge** | Test competing explanations, weak assumptions, source dependence, and realistic failure modes. | A stronger countercase and revised judgments where needed. |
| **Decide** | Compare options, explain tradeoffs, and identify the next useful action. | A recommendation, its uncertainty, and the evidence that would change it. |

The process can loop back when new evidence changes the question. Depth adapts to the task: a narrow fact check receives a focused answer; an ambiguous or consequential decision calls for deeper investigation and challenge.

The skills are reusable instructions and methods for the host agent. The host supplies the AI model, browsing, file access, computation, and any connected services. intel selects methods that fit the question and works with the tools and evidence actually available.

## The ten skills

| Skill | Use it to | Typical output |
|---|---|---|
| [`intel`](skills/intel/SKILL.md) | Frame a complex question and coordinate the relevant workflows. | Investigation plan and integrated judgment. |
| [`intel-research`](skills/intel-research/SKILL.md) | Gather evidence, verify claims, resolve conflicting reporting, and identify gaps. | Source assessment, claim ledger, and research findings. |
| [`intel-diagnose`](skills/intel-diagnose/SKILL.md) | Explain what is causing a problem and test alternative explanations. | Issue tree, competing hypotheses, and discriminating tests. |
| [`intel-compete`](skills/intel-compete/SKILL.md) | Understand a company, industry, market, or competitor. | Competitive assessment and strategic options. |
| [`intel-stakeholders`](skills/intel-stakeholders/SKILL.md) | Understand decision rights, incentives, influence, and dependencies. | Stakeholder map and engagement plan. |
| [`intel-foresight`](skills/intel-foresight/SKILL.md) | Explore plausible futures and forecast clearly defined outcomes. | Scenarios, conditional forecasts, and warning indicators. |
| [`intel-innovate`](skills/intel-innovate/SKILL.md) | Find unmet needs and test new propositions or market opportunities. | Buyer-value hypotheses and experiments. |
| [`intel-risk`](skills/intel-risk/SKILL.md) | Examine failure pathways, exposure, controls, and contingencies. | Risk assessment and proportionate responses. |
| [`intel-red-team`](skills/intel-red-team/SKILL.md) | Challenge a thesis, recommendation, or completed analysis. | Strongest counterargument and corrections. |
| [`intel-brief`](skills/intel-brief/SKILL.md) | Turn findings into a memo, report, or executive readout. | Clear synthesis with traceable support and next steps. |

Start with **intel** when the question spans several areas. Name a specialist when you already know the task, such as “Use intel-red-team to challenge this investment thesis.”

## Try it

**Investigate a company or market**

> Use intel to assess whether this market is attractive for a new entrant. Examine industry economics, competitors, customer needs, barriers to entry, and the strongest reasons the opportunity might fail.

**Find the cause of a problem**

> Use intel-diagnose to investigate why customer retention declined. Compare plausible explanations, identify evidence that distinguishes them, and recommend the next tests.

**Challenge a decision**

> Use intel-red-team to challenge this strategy. Find the strongest counterevidence, identify fragile assumptions, and explain what would change the recommendation.

**Explore uncertainty**

> Use intel-foresight to develop scenarios for this market over the next two years. Explain the drivers, observable warning signs, and actions appropriate to each scenario.

**Turn research into a decision**

> Use intel-brief to turn these documents into a decision memo. Lead with the recommendation, cite the supporting evidence, show the strongest opposing case, and identify unresolved questions.

For better results, include the decision you face, the entities and geography involved, your time horizon, relevant documents, and the output you need.

[More example prompts](docs/examples.md)

## What to expect from an analysis

intel's workflows instruct the agent to:

- Distinguish facts, attributed claims, inferences, assumptions, estimates, forecasts, and recommendations.
- Inspect consequential sources and cite evidence where it supports a claim.
- Check dates, units, denominators, calculations, and whether apparently separate sources share one origin.
- Test a credible alternative explanation and seek evidence against the initial thesis.
- Explain uncertainty, unavailable evidence, and what would change the conclusion.
- Connect findings to concrete choices, tradeoffs, and next actions.

Methods include the intelligence cycle, issue trees and MECE, PESTEL, Porter's five forces, SWOT/TOWS, stakeholder analysis, Blue Ocean strategy, scenario planning, and failure analysis. The coordinator uses them where they help answer the question.

Outputs depend on the host model, available tools, and quality of evidence. The plugin does not guarantee accuracy, provide paid database access, or run background monitoring by itself.

[Evidence standards](skills/intel/references/evidence-standards.md) · [Analytical templates](skills/intel/references/templates.md)

## Documents and reference material

Use intel with documents you provide and sources your agent can access. An optional local index lets the agent search and retrieve pages from an authorized document collection.

The public package includes original workflow instructions, methodological notes, templates, and a bibliography of 28 readings. Third-party PDFs and their full extracted text are not bundled. All ten skills can operate without that original collection; bibliography entries are references, not a claim that the source is available.

[Reading bibliography](skills/intel/references/source-catalog.md) · [Method map](skills/intel/references/method-map.md) · [Local document setup](docs/local-sources.md) · [Source policy](SOURCE_NOTICE.md)

## Install from GitHub

This repository is a marketplace containing the intel plugin. Choose the installation route supported by your host.

### ChatGPT workspace

A workspace admin can use **Admin → Plugins → Add → Import marketplace**:

| Field | Value |
|---|---|
| Source | `https://github.com/kavins06/intel-chatgpt` |
| Path | Leave empty |
| Branch, tag, or commit | `main` |

Authorize GitHub access, review the import, and configure who can install intel. New marketplace connections check for updates daily. Use **Admin → Plugins → Marketplaces → intel → Sync now** for an immediate refresh.

### Desktop / Codex

With a Codex CLI that supports plugin marketplaces:

```bash
codex plugin marketplace add https://github.com/kavins06/intel-chatgpt.git --ref main
```

Restart the ChatGPT desktop app, open the Plugins Directory, select the **intel** marketplace, and install **intel**. Fetch later updates with:

```bash
codex plugin marketplace upgrade intel-chatgpt
```

The marketplace identifier is `intel-chatgpt`; its display name is `intel`. Availability varies by host and account.

### ZIP import

[Download intel v1.2.0](https://github.com/kavins06/intel-chatgpt/raw/refs/heads/main/downloads/intel-1.2.0.zip), attach it in a ChatGPT account with Plugin Creator available, and ask:

> Create a plugin from this intel archive.

ZIP import creates an independent copy. It does not stay synchronized with GitHub. A GitHub marketplace import also does not automatically replace an existing ZIP-created copy.

### Other compatible agents

The root `plugin.json` follows Agent Plugins 1.0. Compatible agents can load the package or its `SKILL.md` workflows. Keep all ten skill directories together because they share references. An explicit starting point is `skills/intel/SKILL.md`.

The instruction workflows need no Python packages or API keys supplied by intel. Optional document utilities require Python 3.10+; PDF indexing uses `pypdf`.

Official setup references: [Workspace import and sync](https://learn.chatgpt.com/docs/enterprise/plugin-management) · [Marketplace packaging and desktop setup](https://developers.openai.com/plugins/build/plugins).

## Develop and contribute

Workflow instructions live in `skills/<name>/SKILL.md`; shared methods and templates live in `skills/intel/references/`. Presentation metadata is in `plugin.json`, and the marketplace entry is in `.agents/plugins/marketplace.json`.

Validate and build from the repository root:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
python3 scripts/package.py --output downloads/intel-1.2.0.zip
```

The package builder uses an explicit file allowlist to exclude private documents, extracted source text, credentials, and repository history. GitHub Actions checks validation, tests, and reproducibility of the downloadable package.

## License

Original code, workflow instructions, and documentation are available under the [MIT License](LICENSE). The supplied image and third-party materials have separate rights described in [SOURCE_NOTICE.md](SOURCE_NOTICE.md).
