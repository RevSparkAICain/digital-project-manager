---
name: connecting-a-tracker
description: "Connect any project tracker that has an MCP server so the pm skills can read and write it; ClickUp, Linear, Jira, Asana and Monday.com have their own agents and only need their profile copied, while any other tracker (Wrike, Smartsheet, YouTrack, GitHub Projects and others) gets the full five steps. Finds the server, adds it, probes it read-only, maps its concepts into a tracker profile, and sets the write rules. Use when a team says which tracker it runs and nothing is connected yet. Writes for the five trackers with agents hand off to updating-trackers."
---

# Connecting a tracker

This skill takes a tracker from "we use it" to "the pm skills can work in it". It ends with a
tracker profile in `trackers.yaml` and an active tracker named in `pm-config.yaml`. The
profile records the tool names the server really offers, so later skills never guess them.

No API key or token goes in chat or in the repo.

## Where files come from

For the profile template and the pod config, use the first of these that exists:

1. the project's own file, if present (`pods/pm/trackers.yaml`, `pods/pm/pm-config.yaml`)
2. otherwise, this folder's shared/ copy (`shared/trackers.example.yaml`,
   `shared/pm-config.example.yaml`)

Files in `shared/` are copies and are never edited. When the project has no `trackers.yaml`,
copy `shared/trackers.example.yaml` to `pods/pm/trackers.yaml` (or to `trackers.yaml` beside
this SKILL.md when the skill is used on its own) and write the profile there. When it has no
`pm-config.yaml`, copy `shared/pm-config.example.yaml` the same way, to `pods/pm/pm-config.yaml`
or beside this SKILL.md.

Prose that goes to people follows `shared/writing-standard.md`.

## Specialist trackers

ClickUp, Linear, Jira, Asana and Monday.com already have an owner for writes: `clickup-agent`,
`linear-agent`, `jira-agent`, `asana-agent` and `monday-agent`. Their profiles in
`trackers.example.yaml` carry `specialist: updating-trackers`. When the user names one of
them, confirm the connection in steps 1 to 3, copy its profile into `trackers.yaml` with
`mcp_server` set to the name `claude mcp list` shows, set `tracker` to the profile name in
`pm-config.yaml`
(copied as above when the project has none), then hand every write to
`updating-trackers` and skip steps 4 and 5. Every other tracker uses the five steps
below with `specialist: none`.

## Steps

### 1. Find

Check which servers are connected: run `claude mcp list` in a terminal, or `/mcp` inside a
session. If the tracker is listed, note the server name exactly as shown and go to step 3.

If it is missing, get the server address from the tracker vendor's own documentation. This
skill carries no vendor address, because addresses change. Ask the user to paste the address
(a public URL is fine to share; a credential is not, and neither is an address that
carries a key or token in it).

### 2. Add

In Claude Code, add the server with:

`claude mcp add --transport http <name> <url>`

Pick a scope with a flag:

- `--scope user`: available in every project on this machine, kept out of the repo.
- `--scope local`: this project only, private to this machine (the default).
- `--scope project`: written to `.mcp.json` at the project root, which is shared with the
  repo. Never put a secret in that file.

In claude.ai, use the connector directory instead and switch the connector on for the
workspace.

Sign in with OAuth: run `/mcp`, choose the server, and finish the browser sign-in. If the
server only accepts an API key, set it as an environment variable on the user's machine and
reference the variable by name in the server config. The user types the key into their own
shell or credential store, never into this conversation. No API key or token goes in chat or
in the repo.

### 3. Probe read-only

1. List the tools the server offers and copy the exact names.
2. Make one read call, for example list the projects the account can see.
3. Record which tool names do what (read, create, update, comment, link).

Nothing is written in this step. If the probe fails (no tools, sign-in error, empty
result), stop, report the exact error text, and fix the connection before going further.

### 4. Map

Open the project's `trackers.yaml`. When the project has none, first copy
`shared/trackers.example.yaml` to `pods/pm/trackers.yaml` (or beside this SKILL.md when the
skill is used on its own); never add the entry to the shared copy. Add one `- name:` entry
there and walk the user through each field:

- `name`, `mcp_server`, `specialist` (`none` unless the tracker has its own agent).
- `concepts`: what the tracker calls a container, an item, a status, an assignee, a due date,
  a milestone and a dependency, or `none` where it has no such thing.
- `read_tools` and `write_tools`: the exact names from the step 3 probe.
- `gaps`: each concept the tracker lacks, and what the skills do instead (for example a group
  named for the milestone).
- `default_container`: where a new item lands when no project is named.

Then set `tracker:` in the project's `pm-config.yaml` to the profile name, copying
`shared/pm-config.example.yaml` to `pods/pm/pm-config.yaml` first when the project has none.
Two filled examples are in `examples/` and are illustrative: replace their tool names with the
ones the probe listed.

### 5. Write rules

Every change to the tracker follows the same path:

1. Build the planned changes as a table: item, change, field values.
2. Show the table. Nothing is written until the user approves the table, or the user's own
   request named that exact change.
3. Write only what the approved table lists, using the profile's `write_tools`.
4. Read each item back with `read_tools` and compare it with the table.
5. Report every difference. Do not fix a difference silently.

Deletes, bulk changes and permission changes need their own explicit go-ahead.

## Output

- A profile entry in `trackers.yaml` with no gaps left unrecorded.
- `tracker:` set in `pm-config.yaml`.
- A short report: server name, tool names found, the probe result, and the gaps.
