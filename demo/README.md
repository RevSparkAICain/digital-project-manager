# Run the demo

The demo hands one recorded call to a copy of this folder that is already set up. The agents
turn it into notes and update five trackers at once while you present the workflow slides.
You pre-approve the creates and updates when you start the run, so it never stops to ask; the
closes wait for you. The offline steps at the end use the ACME example that ships with the
skills.

## Before the day

1. Install Python 3.11 or later. Onboarding checks the packages it needs and offers to install any that are missing.
2. Connect the trackers in Claude: ClickUp, Linear, Jira (Atlassian), Asana and Monday.com. Run
   `claude mcp list` and check every one shows as connected. A connector added later can need
   a restart.
3. **Set up the copy you will present from.** Unzip it, run `claude` in a terminal in that
   folder, say "set me up" and give these answers:

   | Stage | Answer |
   |---|---|
   | 1. About you | Your organization and your name. Approval: "the account director". Escalation: "the pursuit sponsor". RAID: markdown, weekly |
   | 2. What is connected | The table should list all five trackers and your mail connector. Say which ones you want |
   | 3. Trackers | Projects live in different trackers. Building management: Jira. Network design: Linear. LEED advisory: Asana. Specialist outreach: Monday.com. Default: ClickUp, for Pursuit admin. Each tracker then lists its projects, read-only |
   | 4. Transcripts | This folder, `transcripts/inbox/`. Check every 1 minute for the demo |
   | 5. Mail | Skip |
   | 6. Brand | Skip |
   | 7. Checks and watch | The checks report their counts. Watch: "not now"; on stage you start the run by hand |

4. In each tracker, create the demo project, board or list for its workstream and load the
   seed items, as `seed-tasks.md` describes under "Live demo: one call, five trackers".
5. Rehearse "On the day" in that copy. Each time Claude Code asks for permission, answer
   "Yes, and don't ask again", so the live run never stops at a prompt while you are on the
   slides. Then follow "Reset for another run".

No trackers? The notes (step 4) and the health read (step 8) still run, and step 5 shows the
table without applying it.

## On the day

Setup is done, so the audience sees only the agents and skills at work. The demo runs in two
halves around the workflow slides. At slide 6 ("Live demo"), do steps 1 to 3 and switch back
to the slides; processing takes several minutes. At slide 18 ("Back to the demo"), do steps 4
to 8.

1. **Open the prepared copy.** In a terminal in the folder, run `claude`. Setup is complete,
   so it goes straight to work.

2. **Drop the transcript in.** Copy `demo/Sample_Transcript_sanitized.docx` into
   `transcripts/inbox/`.

3. **Say "process new transcripts, pre-approved", then go back to the slides.** "Pre-approved"
   lets it write the creates and the updates on its own; without it, every write waits for you.
   Mention that `/loop 15m process new transcripts` does this on a schedule; on stage a single
   run keeps the table at the bottom of the screen for when you return.

4. **Open the notes.** The call becomes subject blocks with action, decision, question and risk
   registers, saved as a `.docx` in `deliverables/meeting-notes/`. The transcript labels people
   only as Speaker 1 to 4; the notes work out who is who from what was said.

5. **Read the reconciliation table.** Every row names its project and tracker. The creates
   and the updates to existing SUS items are already written across all five trackers, each
   with a link, and each tracker agent read its writes back. Show each board. The closes are
   held, with any row it was unsure of, and the log line stays `waiting`.

6. **Approve the closes by number, and skip one.** Closes always wait for you, even in a
   pre-approved run. The log line changes to `applied` once no row is held.

7. **Ask for this week's status.** "Write this week's status for the Network design project."
   `project-status-reporting` shows the dated status line with a RAG color and posts it after
   you approve.

8. **Run the monthly health read.** It runs offline on a ten-project example portfolio. From
   `.claude/skills/project-portfolio-reporting-health-read/`:

   ```
   python scripts/grade_portfolio.py examples/portfolio-export.json --config examples/demo-config.json --as-of 2030-03-12 --judgments examples/judgments.json --out work/findings.json
   python scripts/build_deck.py work/findings.json --out work/health-read.pptx
   ```

   Expect portfolio grade C with 2 of the 10 projects not current, and an 18-slide deck. The
   first command exits with code 3 and the message "1 item not judged, so the grade is
   provisional"; the example leaves one judgment open on purpose. On Windows, use `py` when
   `python` is not found.

## The ACME example instead

To run the shorter ACME Weekly Ops Sync, load the DEMO items from `seed-tasks.md` and copy
`.claude/skills/meeting-transcript-to-executive-notes/examples/transcript-weekly-ops-sync.txt`
into the inbox at step 2. Its notes have four subject blocks, then 7 actions (one with no owner
yet), 3 decisions, 2 open questions and 3 risks. The transcript says "jeer a migration"; the
notes say Jira migration.

## Reset for another run

- Delete the transcript from `transcripts/inbox/` and its line from `transcripts/processed.log`.
- Move that run's notes `.docx` and its `- reconciliation.md` table out of
  `deliverables/meeting-notes/`.
- Put the seed items back to the statuses in `seed-tasks.md`, and delete the items the run
  created.
- For a fresh onboarding, use a new unzipped copy.
