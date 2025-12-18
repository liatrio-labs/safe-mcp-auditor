from __future__ import annotations

from safe_mcp_auditor.report.models import Evidence, Report, Severity


def _render_evidence_table(evidence: list[Evidence]) -> str:
    if not evidence:
        return "_No evidence provided._"

    lines = [
        "| Path | Lines | Notes |",
        "| --- | --- | --- |",
    ]

    for item in sorted(evidence, key=lambda e: (e.path, e.line_start, e.line_end)):
        lines.append(
            f"| `{item.path}` | {item.line_start}-{item.line_end} | {item.notes} |"
        )

    return "\n".join(lines)


def _render_excerpt_blocks(evidence: list[Evidence]) -> str:
    blocks: list[str] = []
    for item in sorted(evidence, key=lambda e: (e.path, e.line_start, e.line_end)):
        blocks.extend(
            [
                f"**{item.path}:{item.line_start}-{item.line_end}**",
                "```text",
                item.excerpt,
                "```",
                "",
            ]
        )
    return "\n".join(blocks).rstrip()


def render_report_md(report: Report) -> str:
    """Render a deterministic Markdown report from a validated report model."""

    severity_counts = {severity: 0 for severity in Severity}
    for finding in report.findings:
        severity_counts[finding.severity] += 1

    lines: list[str] = []

    lines.append(f"# SAFE-MCP Audit Report: {report.metadata.target_name}")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Status: `{report.status}`")
    lines.append(
        "- Findings: "
        f"{len(report.findings)} (critical: {severity_counts[Severity.CRITICAL]}, "
        f"high: {severity_counts[Severity.HIGH]}, "
        f"medium: {severity_counts[Severity.MEDIUM]}, "
        f"low: {severity_counts[Severity.LOW]})"
    )
    lines.append(f"- Unknowns: {len(report.unknowns)}")
    lines.append("")

    lines.append("## Findings (Prioritized)")
    lines.append("")
    if not report.findings:
        lines.append("_No findings._")
        lines.append("")
    else:
        for finding in report.findings:
            finding_id = finding.id or "(missing-id)"
            lines.append(f"### {finding_id}: {finding.title}")
            lines.append("")
            lines.append(f"- Severity: `{finding.severity}`")
            lines.append(f"- Confidence: `{finding.confidence}`")
            lines.append(
                "- SAFE-MCP Techniques: "
                + (", ".join(finding.safe_mcp.techniques) or "(none)")
            )
            lines.append(
                "- Recommended mitigations: "
                + (", ".join(finding.safe_mcp.recommended_mitigations) or "(none)")
            )
            lines.append("")

            lines.append("**What is happening**")
            lines.append("")
            lines.append(finding.what_is_happening)
            lines.append("")

            lines.append("**Why it matters**")
            lines.append("")
            lines.append(
                "- CIA: "
                f"C={finding.why_it_matters.cia.confidentiality}, "
                f"I={finding.why_it_matters.cia.integrity}, "
                f"A={finding.why_it_matters.cia.availability}"
            )
            lines.append(f"- Scope: {finding.why_it_matters.scope}")
            lines.append("")

            lines.append("**Evidence**")
            lines.append("")
            lines.append(_render_evidence_table(finding.evidence))
            lines.append("")
            lines.append(_render_excerpt_blocks(finding.evidence))
            lines.append("")

            lines.append("**Recommendation**")
            lines.append("")
            lines.append(finding.recommendation)
            lines.append("")

    lines.append("## Quick hardening checklist")
    lines.append("")
    lines.append("- [ ] Triage findings by severity")
    lines.append("- [ ] Address `needs_review` unknowns")
    lines.append("- [ ] Add/verify audit logging for tool calls")
    lines.append("")

    lines.append("## Unknowns / Needs manual review")
    lines.append("")
    if not report.unknowns:
        lines.append("_None._")
        lines.append("")
    else:
        for unknown in report.unknowns:
            unknown_id = unknown.id or "(missing-id)"
            lines.append(f"### {unknown_id}: {unknown.question}")
            lines.append("")
            lines.append(f"- Why it matters: {unknown.why_it_matters}")
            lines.append(f"- How to verify: {unknown.how_to_verify}")
            lines.append(
                "- Related techniques: "
                + (", ".join(unknown.related_techniques) or "(none)")
            )
            lines.append("")
            lines.append("**Evidence**")
            lines.append("")
            lines.append(_render_evidence_table(unknown.evidence))
            lines.append("")
            lines.append(_render_excerpt_blocks(unknown.evidence))
            lines.append("")

    lines.append("## Appendix A: Inventory")
    lines.append("")
    lines.append("### Tools")
    lines.append("")
    if not report.inventory.tools:
        lines.append("_No tools recorded._")
    else:
        for tool in report.inventory.tools:
            lines.append(f"- `{tool.name}`: {tool.description}")
    lines.append("")

    lines.append("## Appendix B: SAFE-MCP technique coverage matrix")
    lines.append("")
    if not report.coverage:
        lines.append("_No coverage recorded._")
    else:
        lines.append("| Technique | Applicability | Confidence | Linked findings |")
        lines.append("| --- | --- | --- | --- |")
        for entry in report.coverage:
            linked = ", ".join(entry.linked_finding_ids) or "(none)"
            lines.append(
                f"| `{entry.technique_id}` | {entry.applicability} | {entry.confidence} | {linked} |"
            )

    return "\n".join(lines).rstrip() + "\n"
