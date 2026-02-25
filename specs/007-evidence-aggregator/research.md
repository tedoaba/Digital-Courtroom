# Research: Evidence Aggregation & Path Safety

## Decision: Path Sanitization Logic

**Decision**: Use `pathlib` and `pathlib.Path().resolve()` to normalize and verify paths.
**Rationale**:

1. `pathlib` provides a cross-platform way to handle paths.
2. C-XV requires list-form arguments and sandboxing. If we later use these paths to read files, they must be secure.
3. `Path(repo_root).joinpath(claimed_path).resolve()` allows us to check if the result starts with `repo_root`.
4. If a path escapes (e.g., `../../etc`), `os.path.commonpath` or `.is_relative_to()` (Python 3.9+) can detect it.

**Alternatives considered**:

- Generic Regex: Brittle, fails with symbolic links or weird encoding.
- `os.path.abspath`: Harder to reason about than `pathlib`.

## Decision: Evidence Deduplication

**Decision**: Use a dictionary-based merge with `evidence_id` as the key, then convert back to the `List[Evidence]` demanded by `AgentState` if needed, although `AgentState.evidences` is `Dict[str, List[Evidence]]`.
**Rationale**:

- `AgentState.evidences` is `Annotated[Dict[str, List[Evidence]], operator.ior]`.
- This means LangGraph _already_ merges the top-level keys (`repo`, `docs`, `vision`).
- The `EvidenceAggregator` receives the _merged_ dictionary.
- We strictly need to deduplicate within each list.
- We will iterate through each list and keep only the latest entry per `evidence_id`.

**Alternatives considered**:

- Set-based deduplication: Requires making Pydantic models hashable (standard but then requires `frozen=True`).
- Manual loop: Simplest to implement without changing `Evidence` models.

## Decision: Hallucination Matching Threshold

**Decision**: Exact matching after normalization.
**Rationale**:

1. Partial matches (e.g., `auth.py` matching `src/auth.py`) are dangerous and can hide actual hallucinations.
2. We require "Relative to Root" paths in documentation.
3. Case-sensitivity: MUST match the file system. In CI/CD (usually Linux), `src/Auth.py` != `src/auth.py`. We will respect this to avoid "it works on my machine" issues.

## Decision: Manifest Extraction

**Decision**: Extract manifest from `repo` evidence items where `evidence_class` is `FILE_METADATA` or similar.
**Rationale**:

1. The `RepoInvestigator` (Layer 1) produces a list of files it examined.
2. We iterate through `evidences["repo"]` and collect all `location` fields into a `set` for O(1) matching.
3. If `evidences["repo"]` is empty, the manifest is empty, triggering SC-001 for all doc claims.

## Decision: Collision Policy

**Decision**: First-write-wins (or log and preserve).
**Rationale**: In a forensic context, if two detectives (e.g., Repo and Docs) both find the "same" evidence (e.g., specific file exists), we should preserve both findings if they have different `source` fields, but if the `evidence_id` is identical, we keep the one from the most "authoritative" detective or just the first one found. Actually, `evidence_id` includes the source (per C-XVI: `{source}_{class}_{index}`), so collisions should only happen if a single detective produces duplicates.

## Decision: Performance Budget

**Decision**: Dictionary merging and list comprehension.
**Rationale**: Python dict lookups are O(1). Merging 1,000 items takes <1ms. String matching for 1,000 paths against 10,000 files in a set is also O(n) and very fast. SC-002 (50ms) is highly achievable. Performance will be verified using `pytest-benchmark` or a simple `time.perf_counter()` block.
