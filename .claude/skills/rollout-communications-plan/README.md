# rollout-communications-plan

Produces the plan that comes before any rollout copy: who is told what, over which channel,
on which day, who approves, who sends, and how the team will check afterward that it
landed. It covers a change profile, an audience matrix ranked Act, Adapt or Aware, a channel
assignment, a dated T-minus send sequence, approvals, measurement, risks and a build list for
the writing and design agents. It plans only and sends nothing.

## Inputs

- The facts of the change: scope, go-live date and time, outage window, who is affected,
  whether action is needed, rollback options, owner and approver.
- `comms-config`: `pods/comms/comms-config.yaml` if the project has one, otherwise
  `shared/comms-config.example.yaml`. It sets the enabled channels, whether an intranet
  exists, which telemetry is available, the time zone and the roles.
- Audiences: `pods/comms/audiences.yaml` if present, otherwise
  `shared/audiences.example.yaml`.
- The writing standard: the installed house-style skill if present, otherwise
  `shared/writing-standard.md`.

## Outputs

- A markdown plan with eight sections, in order: Change profile, Audience matrix, Channels,
  Send sequence, Approvals, Measurement, Risks, Build list, plus open questions. See
  `examples/rollout-plan.md`.
- Saved under `output_dir` as `YYYY-MM-DD-rollout-plan-<topic>.md`.

## How the config shapes the plan

| Setting | Result |
|---|---|
| `intranet.present: false` | Durable references go out as an attached PDF, never a link |
| `telemetry` rates off | The measurement section says rates are not available and uses counts |
| a channel with `enabled: false` | The channel is left out of the matrix |

Files in `shared/` are fallback copies that let this skill run on its own. Your own settings
live in `pods/` and `brand/`; edit those, never the copies.

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | The procedure the agent follows |
| `examples/rollout-plan.md` | A finished ACME plan to copy the shape from |
| `shared/` | Copies of the writing standard, the pod config and the audiences file |
