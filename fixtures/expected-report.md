# SAFE-MCP Audit Report: example-target

## Summary

- Status: `pass`
- Findings: 2 (critical: 0, high: 1, medium: 0, low: 1)
- Unknowns: 0

## Findings (Prioritized)

### F-aaaaaaaaaaaa: High severity finding

- Severity: `high`
- Confidence: `high`
- SAFE-MCP Techniques: SAFE-T0001, SAFE-T0003
- Recommended mitigations: SAFE-M-2

#### What is happening

A high-risk issue was found.

#### Why it matters

- CIA: C=high, I=medium, A=low
- Scope: example

#### Evidence

| Path | Lines | Notes |
| --- | --- | --- |
| `server.py` | 3-3 | Example excerpt |

#### Evidence excerpts

##### server.py:3-3

```text
do_dangerous()
```

#### Recommendation

Fix the issue quickly.

### F-bbbbbbbbbbbb: Low severity finding

- Severity: `low`
- Confidence: `high`
- SAFE-MCP Techniques: SAFE-T0002
- Recommended mitigations: SAFE-M-1

#### What is happening

A low-risk issue was found.

#### Why it matters

- CIA: C=low, I=low, A=low
- Scope: example

#### Evidence

| Path | Lines | Notes |
| --- | --- | --- |
| `app.py` | 10-12 | Example excerpt |

#### Evidence excerpts

##### app.py:10-12

```text
print('hello')
```

#### Recommendation

Fix the issue.

## Quick hardening checklist

- [ ] Triage findings by severity
- [ ] Address `needs_review` unknowns
- [ ] Add/verify audit logging for tool calls

## Unknowns / Needs manual review

_None._

## Appendix A: Inventory

### Tools

- `a-tool`: First tool
- `b-tool`: Second tool

## Appendix B: SAFE-MCP technique coverage matrix

| Technique | Applicability | Confidence | Linked findings |
| --- | --- | --- | --- |
| `SAFE-T0001` | applicable | high | F-aaaaaaaaaaaa |
| `SAFE-T0002` | applicable | high | F-bbbbbbbbbbbb |
| `SAFE-T0003` | applicable | high | F-aaaaaaaaaaaa |
