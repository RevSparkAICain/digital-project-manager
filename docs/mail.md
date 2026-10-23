# Mail threads in the project record

Optional. With a mail connector, project threads join the same loop as meeting transcripts:
the agent reads the threads you allow, ties them to tracked actions, and drafts replies. You
approve every tracker change and you send every email yourself.

## Set it up

1. Connect Microsoft 365 or Gmail in Claude (Settings, then Connectors), or add the vendor's
   MCP server with `claude mcp add`. On a Team or Enterprise plan an Owner or Admin may need to
   add the connector.
2. Run `getting-started` again and pick Stage 5, Mail. It probes the connector read-only,
   records the tool names, and asks which folders, labels or search terms belong to each
   project.

The settings land in the `mail` block of `pods/pm/pm-config.yaml`:

```yaml
mail:
  mcp_server: microsoft-365              # as `claude mcp list` shows it
  read_tools: [outlook_email_search]     # what the probe found
  read_scope:                            # per project
    Jira migration: ["folder: Projects/Jira migration"]
    Monitoring vendor renewal: ["label: vendor-renewal"]
  write: drafts_only
```

`project-manager` holds the instructions for mail (item 7 in its file): it reads only these
threads through these tools, and drafts only when `write` is `drafts_only`.

## What it does

| Step | Who | Result |
|---|---|---|
| Read the threads in `read_scope` | `project-manager` | New asks, dates and decisions per project |
| Match them to tracked actions | `transcript-to-tracked-actions` | A reconciliation table, the same as after a call |
| Apply approved rows | the tracker agent for your tracker | The tracker and the inbox tell the same story |
| Draft a reply | `project-manager` | A draft shown in chat, saved to your Drafts folder only when you approve it, never sent |

## Limits

- Nothing outside `read_scope` is read.
- `write` has two values, `drafts_only` and `off`. No setting sends mail.
- Message bodies stay out of tracker items. A tracked action names the ask and links the
  thread.
