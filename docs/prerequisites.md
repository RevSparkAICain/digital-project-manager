# Prerequisites

Everything an item in this folder needs that the folder does not ship. Install each from its
own source. `getting-started` checks the Python packages before its first question and offers to install any that are missing.

One line installs every Python package below:

```
python -m pip install python-docx python-pptx openpyxl PyMuPDF Pillow
```

On Windows, use `py -m pip` when `python` is not found.

Sankey diagrams (`sankey-chart`) also need matplotlib: `python -m pip install matplotlib`.

## All prerequisites

| Prerequisite | Needed by | Optional? |
|---|---|---|
| Claude Code | Every agent and skill, and `CLAUDE.md` | Required |
| Python 3.11 or later | `brand-extract`. Every other script also runs on 3.9 or later | Required for any script |
| python-docx | `meeting-transcript-to-executive-notes`, `transcript-to-tracked-actions`, `business-case-from-transcript`, `brand-extract` (`template.docx`) | Required to build the meeting notes `.docx` |
| python-pptx | `project-portfolio-reporting-health-read` (`build_deck.py`), `rollout-roadshow-deck` (`build_deck.py`), `sankey-chart` (`to_pptx.py`), `deliverable-review` (content check), `brand-extract` (`template.pptx`) | Required for the health read deck and the roadshow deck |
| openpyxl | `sankey-chart` (reading `.xlsx` rows) | Only for a Sankey diagram from a workbook |
| matplotlib | `sankey-chart` (`sankey.py`) | Only for Sankey diagrams |
| PyMuPDF | `brand-extract` (PDF input), `deliverable-review` (page images) | Required to review `.docx` and `.xlsx` files and to read a PDF brand source |
| Pillow | `brand-extract` (raster logos), `deliverable-review` (content check), `sankey-chart` | Required for the review content check |
| A Chromium-family browser (Edge or Chrome) | `comms-visual-assets` (`render_html.py`, HTML to PNG) | Optional: without one the HTML is delivered unrendered |
| Windows with Microsoft Office | `deliverable-review` and `deliverable-reviewer` (render step) | Rendering is Windows only. On any other system the reviewer marks a file UNREVIEWED and you check it by eye |
| A tracker MCP server | ClickUp: `clickup-agent`. Linear: `linear-agent`. Jira (Atlassian): `jira-agent`. Asana: `asana-agent`. Monday.com: `monday-agent`. Any other: `connecting-a-tracker` | Needed for tracker reads and writes; the notes work without one |
| A meeting connector | The optional transcript pull in `getting-started` (Microsoft 365, Zoom, Google and others) | Optional: a plain folder works without it |
| A mail connector | The optional mail step (Microsoft 365 or Gmail). See `mail.md` | Optional |
| Anthropic `docx`, `pptx` and `xlsx` skills | `pm-analyst` (reports, decks, trackers); `project-status-reporting` (formal memo or slides) | Required by `pm-analyst` for document output. Install them from Anthropic's skills repository on GitHub (`anthropics/skills`) |
| agent-browser (npm) with Node.js | `brand-extract --render`, for pages built by scripts | Optional: only for `--render` |

Credentials never go in chat or in this folder. They stay in the MCP client's own store or in
environment variables.

## By item

| Item | Needs |
|---|---|
| `getting-started`, `house-style` | Nothing beyond Claude Code |
| `project-manager` | A tracker connection, through its tracker agent or a profile from `connecting-a-tracker` |
| `clickup-agent` | ClickUp MCP server |
| `linear-agent` | Linear MCP server |
| `jira-agent` | Atlassian (Jira) MCP server |
| `asana-agent` | Asana MCP server |
| `monday-agent` | Monday.com MCP server |
| `pm-analyst` | A tracker connection; Anthropic `docx`, `pptx` and `xlsx` skills |
| `deliverable-reviewer`, `deliverable-review` | Windows, Microsoft Office, Windows PowerShell, Python with PyMuPDF; python-pptx and Pillow for the content check |
| `meeting-transcript-to-executive-notes` | Python 3.9+ and python-docx |
| `transcript-to-tracked-actions` | Runs `meeting-transcript-to-executive-notes` first; applying approved rows needs a tracker connection with write access |
| `connecting-a-tracker` | An MCP server for the tracker being connected |
| `updating-trackers` | A tracker connection with write access |
| `structuring-linear-projects` | A Linear connection with write access |
| `project-status-reporting` | A tracker connection; optional Anthropic `docx` and `pptx` skills |
| `raid-log-management`, `project-charter-and-kickoff` | A tracker connection for tracker writes; each also writes Markdown with no tracker |
| `business-case-from-transcript` | Python 3.9+ and python-docx |
| `project-portfolio-reporting-health-read` | Python 3.9+ (standard library only for `grade_portfolio.py`); python-pptx for `build_deck.py`. The tracker read goes through the tracker's agent; a ClickUp adapter is included |
| `comms-director`, `comms-strategist`, `comms-copywriter`, `tech-translator`, `rollout-communications-plan`, `it-bulletin`, `leader-cascade-kit` | Nothing beyond Claude Code. Settings in `pods/comms/comms-config.yaml`, falling back to the ACME example |
| `plain-language-translation` | Python 3.9+, standard library only |
| `comms-designer`, `comms-visual-assets` | Python 3.9+; a Chromium-family browser to render PNG |
| `rollout-roadshow-deck` | Python 3.9+ and python-pptx |
| `sankey-chart` | Python 3.9+ with openpyxl, matplotlib, python-pptx and Pillow |
| `brand-extract` | Python 3.11+, PyMuPDF, Pillow, python-pptx, python-docx |
