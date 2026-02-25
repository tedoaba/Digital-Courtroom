# Contract: CLI Interface

## Command Schema

The system is invoked via `uv run` or a direct entry point.

```bash
uv run audit --repo <URL> --spec <PDF_PATH> [--output <DIR>]
```

| Argument          | Flag       | Required | Type  | Default          |
| ----------------- | ---------- | -------- | ----- | ---------------- |
| Repository URL    | `--repo`   | Yes      | `str` | N/A              |
| Specification PDF | `--spec`   | Yes      | `str` | N/A              |
| Output Directory  | `--output` | No       | `str` | `audit/reports/` |

## Exit Codes

| Code | Meaning                                                |
| ---- | ------------------------------------------------------ |
| 0    | Audit completed successfully (Report generated)        |
| 1    | Input validation error (Invalid URL/PDF missing)       |
| 2    | Orchestration timeout (300s limit exceeded)            |
| 3    | Catastrophic internal error (Partial report attempted) |

# Contract: Audit Report Format

## Structure (Markdown)

1. **# Audit Verdict: {RepoName}**
   - Overall Score: {X.X} / 5.0
   - Date: {YYYY-MM-DD}
2. **## Executive Summary**
   - 2-3 sentence overview of findings.
3. **## Criterion Breakdown**
   - One `### {Dimension Name}` section per rubric item.
   - Final Score: {X}
   - Judge Arguments (Pros/Cons/Pragmatic)
   - Dissent Summary (if applicable)
4. **## Remediation Plan**
   - Actionable list of file-level fixes.
5. **## Evidence Appendix**
   - List of all `Evidence` objects cited in the findings.
