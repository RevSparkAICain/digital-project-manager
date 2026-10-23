# project-status-reporting

Produces weekly per-project status and an executive portfolio RAG rollup from tracker data
(ClickUp, Linear, Jira, Asana or Monday.com). It fixes the RAG definitions (green is earned on evidence), a dated-line status
comment format with a worked example, and the rule that fact (tool data) and judgment (the
RAG call) stay separate.

## Inputs
- Meeting notes or a short description of what happened this period.
- Current task data from the tracker (pulled through its agent or `pm-analyst`).
- The project's RAID log (Risks, Actions, Issues, Decisions), when one exists
  (`raid-log-management`, an optional skill; if it is not installed, risks and issues come
  from the meeting notes and tracker data).
- The workspace configuration in `SKILL.md` (status task name, RAG field, RAG source,
  narrative fields).

## Outputs
- A tracker status comment in the house format, posted to the project's status task.
- RAG and narrative field updates on the same task.
- For formal reporting: a branded `docx` memo or 1 to 2 slide `pptx`, reviewed through
  `deliverable-review` before hand-off.
- For portfolios: a one-line-per-project rollup that leads with exceptions.

## How to run
Ask for "this week's status for <project>" or "the portfolio rollup", or invoke the skill by
name. The `project-manager` agent uses it for every status cycle. There is no script.

## Prerequisites
- A tracker connection (ClickUp, Linear, Jira, Asana or Monday.com) with read access (write access to post the comment).
- Optional: the Anthropic `docx` and `pptx` skills for formal output, `brand-extract` (the
  brand skill named in your workspace configuration) for styling, and `deliverable-review`.

Files in `shared/` are fallback copies that let this skill run on its own. Your own settings
live in `pods/` and `brand/`; edit those, never the copies.

## Examples
- `examples/input-meeting-notes.md`: synthetic notes and tracker data for an ACME Co.
  project and a three-project portfolio.
- `examples/expected-status-comment.txt`: the status comment the skill should post.
- `examples/expected-exec-rollup.md`: the portfolio rollup it should return.
