# Digital Project Manager

A Claude Code project folder that runs project management from your meeting transcripts. After
each call it writes the notes, matches the actions against your tracker, and updates the tracker
once you approve. It keeps the RAID log, drafts weekly status, and grades how well every active
project is reported once a month. It works with ClickUp, Linear, Jira, Asana and Monday.com,
and with any other tracker that has an MCP server. When projects live in different trackers, one call
updates all of them, each through its own agent. When a change has to reach the people it
affects, a comms team drafts the rollout plan, the bulletin, the leader packets, the visuals
and a short roadshow deck.

Download it, open it in Claude Code, and say **set me up**. Or give Claude Code this page's
link and ask it to download the folder and set it up.

## The loop

**Call ends** > **Notes written** > **Tasks and RAID** > **Weekly status** > **Monthly health check**

Skills do the work, agents hand it along, and you approve what the agents propose. The
orchestrator is the **Chief of Staff**, or **Chief** for short: during a call, say "Chief,
make that high priority" and it shows up as an instruction in the next reconciliation table.
`docs/workflow.md` shows each step with its skill, agent and hand-off.

## Setup in ten minutes

1. **Install Claude Code and Python 3.11 or later.** On Windows, the Python launcher is `py`;
   use it wherever this folder says `python` if `python` is not found.

2. **Get the folder.** Download the ZIP from the green Code button and unzip it (it unzips to
   `digital-project-manager-main`), or clone it:

   ```
   git clone https://github.com/strategenixsolutions-ux/digital-project-manager.git
   ```

3. **Install the Python packages** the notes and decks use:

   ```
   python -m pip install python-docx python-pptx openpyxl PyMuPDF Pillow
   ```

4. **Open the folder in Claude Code** and say **set me up**. The `getting-started` skill asks a
   few questions, one at a time:
   - your name, your organization, and who approves and who gets escalations (as roles)
   - which trackers, meeting tools, mail and file stores Claude can reach, and how to connect
     the ones you want
   - your tracker or trackers, probed read-only, which project lives where, and where new items
     land
   - where transcripts arrive: this folder (`transcripts/inbox/`), a synced OneDrive, Drive or
     Dropbox folder, or a pull from your meeting connector
   - optional: mail threads and your brand

   It writes nothing to your tracker or mailbox during setup, and no token ever goes in a file.
   If you connect a new server along the way, restart Claude Code and say **set me up** again;
   it picks up where it stopped. It ends by offering the folder watch:
   `/loop 15m process new transcripts`, or a scheduled task on your computer
   (`docs/folder-watch.md`).

Then save a transcript to the inbox, or just say "process new transcripts".

## What is inside

| Path | What it holds |
|---|---|
| `CLAUDE.md` | The Chief of Staff: routes the work, runs approvals, and defines "process new transcripts" |
| `.claude/agents/` | 13 agents: `project-manager`; one tracker agent each for ClickUp, Linear, Jira, Asana and Monday.com (`clickup-agent`, `linear-agent`, `jira-agent`, `asana-agent`, `monday-agent`); `pm-analyst`; `deliverable-reviewer`; the comms team (`comms-director`, `comms-strategist`, `comms-copywriter`, `comms-designer`, `tech-translator`) |
| `.claude/skills/` | 21 skills (below) |
| `pods/pm/`, `pods/meetings/` | Example settings. `getting-started` copies them and fills in what it asks about |
| `pods/comms/` | Example comms settings and audiences for the fictional ACME Co. Copy each to the same name without `.example` and fill in your own |
| `brand/` | The neutral brand every document uses until you run `brand-extract` |
| `demo/` | The webinar run sheet, seed items and sample call, plus the offline ACME example |
| `docs/` | The workflow, the folder watch, mail, prerequisites |

### Skills

| Skill | What it does |
|---|---|
| `getting-started` | Onboarding: finds your connections, sets the tracker and transcript inbox, writes the settings |
| `meeting-transcript-to-executive-notes` | Notes by subject with action, decision, question and risk registers, saved as `.docx` |
| `transcript-to-tracked-actions` | Matches actions to tracked items and shows a table; applies only the rows you approve |
| `updating-trackers` | The rules for every tracker write: real IDs, read first, approval, read back, confirm bulk changes |
| `connecting-a-tracker` | Connects any other tracker with an MCP server, probed read-only first |
| `raid-log-management` | One RAID register per project; each row gets one owner and a dated next step |
| `project-status-reporting` | A dated status line per project and an executive RAG rollup, posted after you approve |
| `project-portfolio-reporting-health-read` | Grades how reliably each project is reported and builds a deck with a fix list per lead |
| `brand-extract` | Reads your website and templates and writes the brand file every document uses |
| `business-case-from-transcript` | A business case `.docx` from a scoping call, with every gap marked |
| `project-charter-and-kickoff` | The charter and kickoff plan from the approved business case |
| `structuring-linear-projects` | Shapes a Linear project: milestones, dependencies, build plan approved first |
| `sankey-chart` | A Sankey flow diagram from spreadsheet rows, as a PNG or one slide |
| `rollout-communications-plan` | Who hears about a change, when, and through which channel |
| `plain-language-translation` | Technical material rewritten for readers outside IT, with a readability check |
| `it-bulletin` | The organization-wide email about a change, in your house format |
| `leader-cascade-kit` | The packet managers use to pass a change down to their teams |
| `comms-visual-assets` | Timelines, before-and-after panels, step flows and one-pagers |
| `rollout-roadshow-deck` | A short deck for a guest slot at another team's meeting |
| `deliverable-review` | The reviewer's procedure: render, then brand, wording and figure checks |
| `house-style` | The writing standard: answer first, banned phrases, no em dashes |

## Ground rules

- Changes the agents work out (from a transcript, mail, a status report or a plan) are shown as
  a table and written only after you approve. A direct request, such as "create a task called
  X", approves exactly that change. Bulk and destructive changes are always confirmed.
- Mail and comms are drafts only. Nothing is ever sent.
- Tokens live in your connector settings or environment variables, never in this folder.
- `.claude/settings.json` lets the agents use the five tracker connectors without a prompt
  each time, and blocks their raw-API write tools. Put rules of your own in
  `.claude/settings.local.json`.
- Transcripts, notes and settings stay out of git (`.gitignore`).

## Requirements

Claude Code, Python 3.11 or later, and an MCP server for your tracker. The document review step
renders files with Microsoft Office on Windows; elsewhere it marks them for you to check by eye.
Full list: `docs/prerequisites.md`.

## License

MIT. See `LICENSE`.
