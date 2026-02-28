import ast
import os
import subprocess
from datetime import datetime

from src.state import ASTFinding, Commit
from src.utils.security import SandboxEnvironment, sanitize_repo_url


def clone_repository(
    repo_url: str,
    dest_dir: str,
    timeout: int = 60,
    sandbox: SandboxEnvironment | None = None,
) -> None:
    """Clones a git repository to a specific directory with a timeout."""
    repo_url = sanitize_repo_url(repo_url)
    cmd = ["git", "clone", repo_url, dest_dir]

    if sandbox:
        result = sandbox.execute_tool(cmd)
        if not result["success"]:
            raise RuntimeError(f"Cloning failed: {result['error']}")
        return

    try:
        subprocess.run(
            cmd,
            check=True,
            timeout=timeout,
            capture_output=True,
            text=True,
        )
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Cloning {repo_url} timed out after {timeout} seconds.") from None
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Cloning failed: {e.stderr}") from e


def get_git_history(
    repo_dir: str,
    limit: int = 50,
    sandbox: SandboxEnvironment | None = None,
) -> list[Commit]:
    """Fetches the git commit history."""
    cmd = [
        "git",
        "log",
        f"-n{limit}",
        "--oneline",
        "--reverse",
        "--format=%H|%an|%at|%s",
    ]

    if sandbox:
        result = sandbox.execute_tool(cmd)
        if not result["success"]:
            return []
        stdout = result["output"]
    else:
        try:
            # Get formatted history: Hash|Author|UnixTime|Message
            res = subprocess.run(
                cmd,
                cwd=repo_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            stdout = res.stdout
        except subprocess.CalledProcessError:
            return []

    commits = []
    if not stdout.strip():
        return commits

    for line in stdout.strip().split("\n"):
        parts = line.split("|", 3)
        if len(parts) == 4:
            commits.append(
                Commit(
                    hash=parts[0],
                    author=parts[1],
                    date=datetime.fromtimestamp(int(parts[2])),
                    message=parts[3],
                ),
            )
    return commits


def analyze_ast_for_patterns(repo_dir: str) -> list[ASTFinding]:
    """Scans Python files for Pydantic models (BaseModel) and LangGraph (StateGraph)."""
    findings = []
    for root, _, files in os.walk(repo_dir):
        if "/." in root.replace("\\", "/") or "\\." in root:
            continue
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, repo_dir)
                try:
                    with open(full_path, encoding="utf-8") as f:
                        content = f.read()
                    tree = ast.parse(content, filename=full_path)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            for base in node.bases:
                                if isinstance(base, ast.Name) and base.id in (
                                    "BaseModel",
                                    "StrictModel",
                                ):
                                    findings.append(
                                        ASTFinding(
                                            file=rel_path,
                                            line=node.lineno,
                                            node_type="ClassDef",
                                            name=node.name,
                                            details={"base": base.id},
                                        ),
                                    )
                        elif isinstance(node, ast.Call):
                            if isinstance(node.func, ast.Name) and node.func.id == "StateGraph":
                                findings.append(
                                    ASTFinding(
                                        file=rel_path,
                                        line=node.lineno,
                                        node_type="Call",
                                        name="StateGraph",
                                        details={},
                                    ),
                                )
                except Exception:
                    pass
    return findings


def check_tool_safety(repo_dir: str) -> list[ASTFinding]:
    """Checks for prohibited operations like os.system or eval."""
    findings = []
    for root, _, files in os.walk(repo_dir):
        if "/." in root.replace("\\", "/") or "\\." in root:
            continue
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, repo_dir)
                try:
                    with open(full_path, encoding="utf-8") as f:
                        content = f.read()
                    tree = ast.parse(content, filename=full_path)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Call):
                            if isinstance(node.func, ast.Attribute):
                                if (
                                    isinstance(node.func.value, ast.Name)
                                    and node.func.value.id == "os"
                                    and node.func.attr == "system"
                                ):
                                    findings.append(
                                        ASTFinding(
                                            file=rel_path,
                                            line=node.lineno,
                                            node_type="Call",
                                            name="os.system",
                                            details={},
                                        ),
                                    )
                            elif isinstance(node.func, ast.Name) and node.func.id == "eval":
                                findings.append(
                                    ASTFinding(
                                        file=rel_path,
                                        line=node.lineno,
                                        node_type="Call",
                                        name="eval",
                                        details={},
                                    ),
                                )
                except Exception:
                    pass
    return findings
