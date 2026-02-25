import ast
import time
from pathlib import Path
from typing import List, Union

from src.models.forensic import ASTFinding
from src.tools.base import ToolResult
from src.tools.utils import with_timeout


def _get_base_names(bases: List[ast.expr]) -> List[str]:
    names = []
    for base in bases:
        if isinstance(base, ast.Name):
            names.append(base.id)
        elif isinstance(base, ast.Attribute):
            names.append(base.attr)
    return names

def _analyze_file(filepath: Path) -> List[ASTFinding]:
    findings = []
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=filepath.name)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = _get_base_names(node.bases)
                findings.append(ASTFinding(
                    file=filepath.name,
                    line=node.lineno,
                    node_type="ClassDef",
                    name=node.name,
                    details={"bases": bases}
                ))
            elif isinstance(node, ast.FunctionDef):
                findings.append(ASTFinding(
                    file=filepath.name,
                    line=node.lineno,
                    node_type="FunctionDef",
                    name=node.name,
                    details={}
                ))
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and "StateGraph" in node.func.id:
                    findings.append(ASTFinding(
                        file=filepath.name,
                        line=node.lineno,
                        node_type="Call",
                        name="StateGraph",
                        details={}
                    ))
                elif isinstance(node.func, ast.Attribute) and "StateGraph" in node.func.attr:
                    findings.append(ASTFinding(
                        file=filepath.name,
                        line=node.lineno,
                        node_type="Call",
                        name="StateGraph",
                        details={}
                    ))
    except SyntaxError as e:
        findings.append(ASTFinding(
            file=filepath.name,
            line=e.lineno or 0,
            node_type="SyntaxError",
            name="SyntaxError",
            details={"msg": str(e)}
        ))
    except Exception as e:
        # Ignore other internal errors
        pass
        
    return findings


@with_timeout(seconds=60)
def scan_repository(repo_path: Union[str, Path]) -> ToolResult[ASTFinding]:
    """
    Scans a repository for code structures without executing code.
    Ref: FR-004 (only static extraction), FR-012 (handling symlinks implicitly by resolving).
    """
    start_time = time.time()
    repo_path = Path(repo_path)
    
    if not repo_path.exists():
         return ToolResult(status="failure", error="Repository path does not exist.")

    all_findings = []
    
    # Simple walk of .py files. To avoid infinite loops via recursive symlinks (FR-012),
    # we maintain a set of visited canonical paths.
    visited_paths = set()
    
    for py_file in repo_path.rglob("*.py"):
        try:
            canonical_path = py_file.resolve(strict=True)
            if canonical_path in visited_paths:
                continue
            visited_paths.add(canonical_path)
            
            file_findings = _analyze_file(canonical_path)
            all_findings.extend(file_findings)
        except Exception:
            # Skip unresolvable paths
            continue

    return ToolResult(
        status="success",
        data=all_findings,
        execution_time=time.time() - start_time
    )
