# Data Model: Sandboxed Forensic Execution Interfaces

## Entities

### Evidence (BaseModel)

_Represents a persistent forensic fact._

- `evidence_id`: str (Format: `{source}_{class}_{index}`)
- `source`: Literal["repo", "docs", "vision"]
- `evidence_class`: Enum (GIT_FORENSIC, STATE_MANAGEMENT, etc.)
- `goal`: str (What was being searched for)
- `found`: bool (Existence of target)
- `content`: Optional[str] (Snippet or path)
- `location`: str (File path, commit hash, or page)
- `rationale`: str (Why this was findings)
- `confidence`: float (0.0 - 1.0)
- `timestamp`: datetime (Data-derivation timestamp)

### Commit (BaseModel)

_Metadata for a single git commit._

- `hash`: str
- `author`: str
- `date`: datetime
- `message`: str

### ASTFinding (BaseModel)

_Metadata for a code structure._

- `file`: str
- `line`: int
- `node_type`: str (e.g., "TypedModel", "StateGraph", "GraphWiring")
- `name`: str
- `details`: Dict[str, Any] (e.g., fields, bases, arguments)

### ToolResult (Generics)

_Wrapper for a tool execution._

- `status`: Literal["success", "failure", "timeout", "disk_limit_exceeded", "access_denied", "network_failure"]
- `data`: T (Optional list of findings)
- `error`: Optional[str]
- `execution_time`: float (For logging only, not for evidence)
