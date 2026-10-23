# leader-cascade-kit

Builds the packet a department leader uses to carry a technology change to their team: a
manager email, a dated ask, spoken talking points, a forwardable blurb, an objection FAQ, a
team meeting script and a readiness checklist. Three tiers (light, standard, heavy) set how
much of the kit a change gets. It drafts only and never sends.

## Inputs

- The message core from `plain-language-translation` (or the short form in `SKILL.md`).
- The change, the go-live date, the departments and the tier.
- `comms-config`: `pods/comms/comms-config.yaml` if present, otherwise
  `shared/comms-config.example.yaml`.
- Audiences: `pods/comms/audiences.yaml` if present, otherwise
  `shared/audiences.example.yaml`.

## Outputs

- A markdown packet with `## Manager email`, `## Talking points`, `## FAQ` and
  `## Team meeting script` blocks, plus the ask, blurb and checklist. See
  `examples/cascade-packet.md`.
- Saved under `output_dir` as `YYYY-MM-DD-leader-cascade-<topic>.md`.

## Checking a packet

From this folder:

```
python shared/check_message.py examples/cascade-packet.md --grade 10 --allow AM,PM,IT,ACME,FAQ
```

The script prints a JSON report and exits 0 when every check passes.

Files in `shared/` are fallback copies that let this skill run on its own. Your own settings
live in `pods/` and `brand/`; edit those, never the copies.

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | The procedure the agent follows |
| `examples/cascade-packet.md` | Worked packet for an ACME change |
| `shared/` | Copies of the writing standard, pod config, audiences file and readability script |
