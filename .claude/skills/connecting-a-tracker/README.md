# connecting-a-tracker

Connects any project tracker that has an MCP server so the other pm skills can read and write
it. The result is a profile in `trackers.yaml` and a `tracker:` setting in `pm-config.yaml`.
No script; the agent runs the steps with the user.

## The five steps

1. **Find** the server with `claude mcp list` or `/mcp`.
2. **Add** it with `claude mcp add --transport http`, then sign in with OAuth.
3. **Probe** it read-only: list its tools, make one read call.
4. **Map** its concepts and gaps into a tracker profile.
5. **Write** only after the user approves the planned-changes table, then read back.

ClickUp, Linear, Jira, Asana and Monday.com have their own agents and are handed to `updating-trackers`.

## Inputs
- The name of the tracker and, if it is not yet connected, its MCP server address from the
  vendor's documentation.

## Outputs
- A tracker profile entry and the active tracker in the pod config.

## Prerequisites
- Claude Code with the `claude mcp` commands, or a claude.ai workspace with connectors.
- An account on the tracker with access to the projects in scope.

## Examples
- `examples/profile-jira.example.yaml`: an illustrative profile from the full five steps, shown
  for Jira. The shipped `jira` profile in `pods/pm/trackers.example.yaml` is the one to use.
- `examples/profile-monday.example.yaml`: the same for Monday.com.

## Shared files
Files in `shared/` are fallback copies that let this skill run on its own. Your own settings
live in `pods/` and `brand/`; edit those, never the copies.
