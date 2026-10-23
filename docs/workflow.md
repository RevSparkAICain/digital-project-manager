# The workflow

Every call feeds one loop that keeps the tracker true:

**Call ends** > **Notes written** > **Tasks and RAID** > **Weekly status** > **Monthly health check**

Skills do the work, agents hand it along, and you approve every write. Each step below lists the
skill that does it, the agent that runs it, and what it hands to the next step.

## 1. Transcripts turn into tracker updates

| Step | Skill | Agent | Hands on |
|---|---|---|---|
| Transcript saved to the inbox | `/loop` or a scheduled task (see `folder-watch.md`) | | Raw transcript or rough notes |
| Notes written by subject | `meeting-transcript-to-executive-notes` | `project-manager` | Action, decision and risk lists, and a `.docx` |
| Actions matched to the tracker | `transcript-to-tracked-actions` | `project-manager` | A numbered table of proposed changes |
| You approve; the tracker updates | `updating-trackers` | the tracker's agent, or its profile | Items created, updated or closed |

When projects live in different trackers (`project_trackers` in `pods/pm/pm-config.yaml`), each
row goes to its project's tracker, and the tracker agents write in parallel. One call can update
Jira, Linear, Asana and Monday.com at once.

## 2. Notes feed tasks and the RAID log side by side

| Step | Skill | Agent | Hands on |
|---|---|---|---|
| Actions become tasks | `transcript-to-tracked-actions` | the tracker's agent, or its profile | Approved tasks created or updated in place |
| Risks, issues and decisions go to RAID | `raid-log-management` | `project-manager` | One owner and a dated next step per row |

Both read the same notes. ClickUp, Linear, Jira, Asana and Monday.com each write through their
own agent; any other tracker writes through the profile `connecting-a-tracker` saves.

## 3. Status calls become rapid fire

Walk the board one person at a time and talk through each item. Nobody types during the call.

| Step | Skill | Agent | Hands on |
|---|---|---|---|
| Walk the board | | | Call transcript with spoken updates |
| Transcript read against existing actions | `transcript-to-tracked-actions` | `project-manager` | Proposed updates matched to tracked items |
| Approve the rows after the call | `updating-trackers` | the tracker's agent, or its profile | The tracker matches what was said |

Quick moves (drag a card, change one status or date) stay live in the tracker. Long readouts,
updates across many items, and follow-ups nobody wrote down go to the agent.

## 4. Weekly status writes itself from the notes

| Step | Skill | Agent | Hands on |
|---|---|---|---|
| Status drafted per project | `project-status-reporting` | `project-manager` | A dated status line with a RAG color |
| Posted where the team looks, after you approve | `updating-trackers` | the tracker's agent | A comment on the project's status task (in Asana, a project status update) |
| Rolled up across projects | `project-status-reporting` | `pm-analyst` | An executive RAG summary |

Inputs: the week's notes, the tracker data and the RAID rows.

## 5. A monthly check audits every active project

| Step | Skill | Agent | Hands on |
|---|---|---|---|
| Pull the portfolio from the tracker | `project-portfolio-reporting-health-read` | the tracker's agent | Tracker export (ClickUp adapter included) |
| Grade how each project is reported | `project-portfolio-reporting-health-read` | `pm-analyst` | Findings per project and per lead |
| Each lead gets a fix list | `project-portfolio-reporting-health-read` | `pm-analyst` | A deck: summary, scorecard, fixes per lead |

It grades how each project is reported, so a late project reported honestly passes.

## 6. Mail threads join the project record (optional)

See `mail.md`. `project-manager` reads the threads you allow, ties them to tracked actions, and
drafts replies. You approve every change and send every email.

## The project lifecycle around the loop

`project-manager` also runs a project from start to close with four skills, in order:

1. `business-case-from-transcript`: a business case `.docx` from the scoping call.
2. `project-charter-and-kickoff`: the charter and kickoff plan, sent to your approval gate.
3. `raid-log-management`: the RAID log, kept for the life of the project.
4. `rollout-communications-plan`, run by `comms-director`: who hears about the change, when
   and through which channel. The comms agents then draft the bulletin, leader packets,
   visuals and roadshow deck for you to send.

Every finished document goes through `deliverable-reviewer` before you see it.
