---
name: getting-started
description: "Onboarding for a new copy of this folder. Interviews the project manager one question at a time, finds which trackers, meeting tools, mail and file stores Claude can reach, connects the tracker read-only, sets where transcripts arrive and how often they are checked, and writes the pod config files. Use on first open (no pods/pm/pm-config.yaml, or setup_complete is not true), or when the PM says set me up, onboard me, run onboarding again, or change where transcripts go."
---

# Getting started

This skill takes a fresh copy of the folder to a working setup for one project manager (the PM).
It ends with the config files, a transcript inbox, a check run, a one-page summary of every
setting it wrote, and the folder watch.

## Rules

- **One question at a time.** Offer the detected or default answer first, so the PM can answer
  yes. Put several choices in a short numbered list.
- **Nothing is written to a tracker or a mailbox during onboarding.** The only calls to a
  connected tool are read calls that prove the connection works.
- **No secret in chat or in a file.** Connections are made through Claude's connector settings
  or `claude mcp add`, with any token held in an environment variable. If the PM starts to paste
  a key, or a server address that carries one, stop them and point to the connection steps.
- **Roles in config.** Approval and escalation are recorded as roles ("the
  project sponsor"). The one name in config is `prepared_by`, the PM's own, in a file that
  stays out of git.
- **Show, then write.** At the end of each stage, show the values you are about to write and
  write them only after the PM says yes.
- **Resume, then re-run.** After each stage, write its number to `setup_stage` in
  `pm-config.yaml`; a skipped optional stage counts as done. When `setup_complete` is not
  `true`, resume at the stage after `setup_stage`, and always run Stage 2 again, because a
  restart is how new connections appear. When it is `true`, show the current values grouped by stage and ask
  which stage to redo. Change only that stage.

## Files this skill writes

| File | Made from | What it holds |
|---|---|---|
| `pods/pm/pm-config.yaml` | `pods/pm/pm-config.example.yaml` | setup flag, `prepared_by`, output folder, approval gate, escalation role, RAID store, active tracker, mail |
| `pods/pm/trackers.yaml` | `pods/pm/trackers.example.yaml` | each tracker in use: server name, tool names, default container |
| `pods/meetings/meetings-config.yaml` | `pods/meetings/meetings-config.example.yaml` | notes folder, transcript inbox and pull, default ClickUp list or Linear team |
| `brand/brand.json` | the existing file | `meta.organization`, or the full brand when `brand-extract` runs |

It also creates `transcripts/inbox/`, `deliverables/` and `work/` when they are missing. Copy
each example file once, then edit the copy. Never edit an `.example` file. Values the PM is not
asked about keep the example's value, except the ACME tracker defaults, which are cleared.

## Before Stage 1. Python packages

On every start, resume included, run `python -c "import docx, pptx, openpyxl, fitz, PIL"`
before the first question (on Windows, `py` in place of `python` when `python` is not found).
When a package is missing, name it and offer to install the missing ones with
`python -m pip install <packages>`, using the names in `docs/prerequisites.md` (python-docx,
python-pptx, openpyxl, PyMuPDF, Pillow). Install only on a yes, then run the check again. On a
no, or when Python itself is missing, say what will not work without it, point to
`docs/prerequisites.md` and carry on.

## Stage 1. About you

Ask, in order:

1. The organization name. Write it to `meta.organization` in `brand/brand.json`.
2. The PM's own name. Write it to `prepared_by`; it signs the notes and "Prepared by" lines.
3. Who approves a business case or charter, as a role. Default: "the sponsor review".
   Writes `approval_gate`.
4. Who a RAID escalation goes to, as a role. Default: "the project sponsor". Writes
   `escalation_role`.
5. Where the RAID log lives: `markdown` (default), `xlsx`, or `tracker`, and how often it is
   reviewed (default `weekly`).

Keep `output_dir` at the defaults (`deliverables/projects`, `deliverables/meeting-notes`) unless
the PM names another folder.

## Stage 2. What is connected

1. Run `claude mcp list`. Also look at the tools this session can call: a connector added on
   claude.ai shows up as tools named `mcp__claude_ai_<Name>__...`.
2. Sort what you find into this table and show it:

   | Need | Examples | Found |
   |---|---|---|
   | Tracker | ClickUp, Linear, Jira, Asana, Monday.com | |
   | Meeting transcripts | Microsoft 365 (Teams), Zoom, Google Drive (Meet), Otter, Fireflies | |
   | Mail (optional) | Microsoft 365 (Outlook), Gmail | |
   | Files (optional) | SharePoint or OneDrive, Google Drive, Dropbox | |

   A server that `claude mcp list` shows as failed or needing authentication counts as not
   found. Say which, so the PM can fix it.
3. Ask which missing ones the PM wants. For each, give the two ways to connect and wait:
   - **Claude app connector:** Settings, then Connectors. On a Team or Enterprise plan only an
     Owner or Admin can add a custom connector, so the PM may need to ask their admin.
   - **Claude Code:** `claude mcp add` with the server address from the vendor's own MCP
     documentation. Do not guess an address. Any token goes in an environment variable.
4. A new server or a new environment variable is only seen after Claude Code restarts. Before
   the PM restarts, confirm Stage 1 is saved and tell them to say **set me up** again
   afterwards; the skill resumes here.
5. Carry on with what is connected. A missing optional item never blocks the next stage.

## Stage 3. Tracker

1. If one tracker is connected, propose it. If several are, ask whether every project lives in
   one tracker or projects live in different ones. One tracker: set `tracker`. Several: set
   `tracker` to the default, ask which tracker each active project lives in, and write the
   answers to `project_trackers`. If none is connected, say the meeting notes still work and
   tracker updates wait until one is, then go to Stage 4. Run steps 2 to 6 for each tracker
   in use.
2. ClickUp, Linear, Jira, Asana and Monday.com each have a tracker agent (`clickup-agent`,
   `linear-agent`, `jira-agent`, `asana-agent`, `monday-agent`). Copy the tracker's profile
   from `pods/pm/trackers.example.yaml` into `pods/pm/trackers.yaml`, set `mcp_server` to the
   name `claude mcp list` shows, and set `tracker` in `pm-config.yaml`. Any other tracker goes
   to `connecting-a-tracker`, which probes it and writes a new profile.
3. Ask the tracker agent for one read-only call that proves access: list the projects,
   boards or teams the account can see. Show up to ten names.
4. Ask where a new item lands when no project is named (a list, team, project or board). For
   ClickUp or Linear, write it to `trackers.clickup_list` or `trackers.linear_team` in
   `meetings-config.yaml`; for any other tracker, write it to `default_container` in its
   profile. Clear the ACME example values the PM did not choose.
5. Ask the tracker agent to list up to five open items in that container, title and status
   only.
6. Offer to deny the server's raw-API write tools in `.claude/settings.local.json`: Jira's
   `executeWrite` and `executeDestructive`, Monday.com's `all_api_write`, `all_monday_api` and
   `execute_code`. Write the rules only on a yes.

## Stage 4. Transcripts

1. Ask which tools the team records meetings in, and where transcripts end up today.
2. Set the inbox. Offer three choices:
   1. **This folder** (default): `transcripts/inbox/`. The PM drops or saves files there.
   2. **A synced folder that already receives transcripts** (OneDrive, Google Drive, Dropbox).
      Take the path, check it exists, and report how many files of the accepted types it holds.
      The inbox is only read. Nothing in it is ever moved, renamed or deleted, so a folder other
      people use is safe.
   3. **Pull from a meeting connector** (offer only when Stage 2 found one). Keep choice 1 as
      the inbox and fill the `pull` block (see below).
3. Refuse an inbox that is the notes folder or sits inside `deliverables/`: saved notes would
   be read back in as new transcripts.
4. When the inbox already holds files, ask whether to process them or start from today. To
   start from today, add one line per existing file to `transcripts/processed.log` with the
   status `skipped at setup`.
5. Accepted file types default to `.vtt`, `.docx`, `.txt` and `.md`. Ask only if the team uses
   something else.
6. Set how often to check. Default `15m`. Writes `check_every`.
7. Write the `ingest` block in `meetings-config.yaml`. The log stays at
   `transcripts/processed.log`.

**Pull setup.** Probe the meeting connector read-only, the way `connecting-a-tracker` probes a
tracker:

1. List the tools the server offers and copy the exact names that find meetings and read a
   transcript. Write them to `pull.read_tools`.
2. Make one read call that lists recent meetings with transcripts. Show title and date only,
   never transcript content.
3. Ask which meetings to pull: one series, meetings the PM organized, or all meetings the PM
   attended. Writes `pull.scope`. Default `since` to today.
4. Set `pull.enabled: true` and `pull.mcp_server`.

If the probe finds no tool that returns transcript text, say so, leave `pull.enabled: false`,
and keep the folder inbox.

Transcripts carry people's words and names. The inbox, the log and `deliverables/` stay out of
git through `.gitignore`.

## Stage 5. Mail (optional)

Skip this stage when Stage 2 found no mail connector or the PM says no.

1. Probe read-only: list the tools and make one call that lists the five newest message
   subjects in one folder. Write the tool names to `mail.read_tools` and the server to
   `mail.mcp_server`.
2. For each active project, ask which folders, labels or search terms belong to it. Write them
   to `mail.read_scope`, keyed by project name. The agent reads nothing outside it.
3. `mail.write` stays `drafts_only`: the agent drafts replies and saves a draft only after the
   PM approves it. `off` turns drafting off. There is no setting that sends.

## Stage 6. Brand (optional)

Ask for the organization's website address or a template file (`.pptx`, `.docx` or `.pdf`).
With either one, run `brand-extract` with the organization name from Stage 1. With neither,
keep the neutral look.

## Stage 7. Check, summary and watch

Run each check and report what it measured, so a zero means something:

1. **Prerequisites.** Run the check from "Before Stage 1" again and report the result.
2. **Notes.** Build the notes skill's sample, `examples/expected-notes.md`, with its
   `scripts/md2docx.py` into `<WORKSPACE_ROOT>/work/`, using `prepared_by` as the operator. Report the file name.
   It stays out of the notes folder, so the demo's transcript is still new.
3. **Tracker.** One read call through the tracker agent. Report the count of items read.
4. **Inbox.** List the accepted files in the inbox and how many are not yet in the log.
5. **Pull.** When enabled, one read call. Report the count of meetings found since `since`.

Show the summary: one table with every setting written, grouped by file. Then set
`setup_complete: true` in `pm-config.yaml`.

**Start the watch last.** Give the PM both options with their own interval filled in, and let
them pick. Do not create a scheduled task without a yes.

- While Claude Code is open: `/loop 15m process new transcripts`
- Unattended, on this computer: a scheduled task that runs `claude -p "process new
  transcripts"` in this folder. Steps are in `docs/folder-watch.md`.

Close with the next step: "Save a transcript to the inbox, or say: process new transcripts."

## Output

- the config files above, each written only after the PM approved that stage
- `transcripts/inbox/`, `deliverables/` and `work/`
- the check results, the settings summary and the chosen watch, in chat
