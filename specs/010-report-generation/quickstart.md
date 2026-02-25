# Quickstart: Generating Reports

The `ReportGenerator` is the final stage of the Digital Courtroom pipeline.

## Manual Trigger (Testing)

If you have a saved `AgentState` or a serialized `AuditReport` object, you can trigger the generator independently of the full graph:

```python
from src.nodes.justice import report_generator
from src.state import AgentState

# Load your state
state: AgentState = load_state("last_run_state.pkl")

# Generate the report
new_state = report_generator(state)

print(f"Report generated at: audit/reports/{state['repo_url']}/report.md")
```

## Verifying Output

1. **Markdown Review**: Open the `.md` file in a viewer (VS Code, GitHub).
2. **Schema Check**: Ensure `run_manifest.json` matches the Pydantic schema for `AgentState`.
3. **Citation Integrity**: Verify that IDs like `repo_git_001` in the text match the ID in the forensic manifest.

## Troubleshooting

- **Empty Report**: Ensure `ChiefJustice` has populated the `final_report` field in the state.
- **Path Errors**: Check write permissions in the `audit/` directory.
- **Template Errors**: Verify `src/templates/report.md.j2` exists and has no syntax errors.
