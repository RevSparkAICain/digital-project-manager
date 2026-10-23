# Watching the transcript inbox

The meeting loop starts when a transcript lands in the inbox that `getting-started` set
(`ingest.inbox` in `pods/meetings/meetings-config.yaml`). Two ways to check it on a schedule,
both on your own computer: the first while you work, the second when Claude Code is closed.

Both send the same prompt, `process new transcripts`. `CLAUDE.md` defines what that does: pull
from the meeting connector when one is set, find inbox files not yet in the log, write the
notes and the reconciliation table for each, and log them. A check that finds nothing replies
with one line.

Cloud schedules (`/schedule`, Claude Code on the web) run against the GitHub copy of this
folder. They cannot see your inbox or your settings, which stay on your computer, so they do
not work for this.

## While Claude Code is open: /loop

```
/loop 15m process new transcripts
```

Use the interval from `ingest.check_every`. The loop runs until you stop it or close the
session. Approve each table as it comes up, and the tracker updates in the same session.

## Unattended: your computer's scheduler

Use Windows Task Scheduler, cron or launchd to run Claude Code non-interactively from this
folder:

```
claude -p "process new transcripts"
```

- **Start it in this folder** so `CLAUDE.md` and the settings load.
- **Run it only while you are logged on.** The review step renders documents with Microsoft
  Office, which does not run in a background session. In Task Scheduler, choose "Run only when
  user is logged on".
- **Allow the tools it needs, and only those,** in `.claude/settings.local.json` (it stays out
  of git), or the run stops at its first permission prompt with nobody there to answer. See
  the Claude Code permissions documentation for the rule syntax. It needs:
  - reading the inbox, and writing to `deliverables/`, `work/` and `transcripts/processed.log`
  - running the skills' Python scripts and, on Windows, the PowerShell render script
  - the tracker's read tools, to match actions to tracked items
  - the meeting connector's read tools, when the pull is on
- **Never allow** the tracker's write tools or any mail tool for unattended runs. Deny them in
  the same file.

An unattended run saves the notes and each reconciliation table, logs the table as `waiting`,
and stops. Nothing is written to a tracker. The next time you open Claude Code here, it lists
the waiting tables and offers to review them.

## What the check never does

- It never moves, renames or deletes a file in the inbox. Handled files are tracked in the log,
  so a shared OneDrive or Drive folder is safe to use as the inbox.
- It never writes to a tracker or mailbox without your approval.

## Starting over on a transcript

Delete its line from `transcripts/processed.log`. The next check treats it as new.
