# Contract: Audit Report Markdown Structure

The `ReportGenerator` MUST produce a Markdown file following this structured contract.

## 1. Document Header

- **Format**: `# Audit Report: {RepoName}`
- **Metadata Table**: Table containing Run Date (ISO8601), Git Hash, Rubric Version, and Aggregate Score.

## 2. Executive Summary

- **Header**: `## Executive Summary`
- **Content**: The `executive_summary` string from `AuditReport`.
- **Scorebox**: Visual representation of the score (e.g., `[ 4.2 / 5.0 ]`).

## 3. Criterion Breakdown

- **Loop**: For each `CriterionResult`:
  - `### {Dimension Name} - Score: {FinalScore}/5`
  - **Verdict**: The synthesized score rationale.
  - **Judicial Debate** (Collapsible):
    - `Prosecutor`: {Argument} (Cites: {EvidenceIDs})
    - `Defense`: {Argument} (Cites: {EvidenceIDs})
    - `Tech Lead`: {Argument} (Cites: {EvidenceIDs})
  - **Dissent Summary** (If variance > 2): Blockquote with `dissent_summary`.
- **Judicial Note** (If variance == 0 but dissent exists): Noted within judicial debate block.

## 4. Remediation Plan

- **Header**: `## Remediation Plan`
- **Loop**: Grouped by Criterion ID.
  - `**{Dimension Name}**`: Bulleted list of instructions from `remediation`.

## 5. Forensic Evidence Manifest

- **Header**: `## Forensic Evidence Manifest`
- **Table**:
  | ID | Source | Location | Rationale |
  |----|--------|----------|-----------|
  | {id} | {source} | {location} | {rationale} |

## 6. Checksum Log (Forensic Integrity)

- **Header**: `## Checksum Log`
- **Implementation**:

  ````markdown
  <details>
  <summary>View Raw Forensic Data (JSON)</summary>

  ```json
  [
    { "evidence_id": "...", ... }
  ]
  ```
  ````

  </details>
  ```

## Output Artifacts

- **Primary**: `report.md`
- **Secondary**: `run_manifest.json` (Machine-readable copy of the state and report metadata).
