from pathlib import Path


def test_directory_structure():
    """Verify that all required directories exist as per Appendix A."""
    required_dirs = [
        "src",
        "src/nodes",
        "src/tools",
        "tests",
        "audit",
        "rubric",
    ]

    for d in required_dirs:
        # Check relative to repo root (which is cwd during uv run pytest)
        assert Path(d).is_dir(), f"Directory {d} is missing"


def test_core_files_exist():
    """Verify that core foundational files exist."""
    required_files = [
        "src/config.py",
        "src/state.py",
        "src/graph.py",
        "pyproject.toml",
        ".gitignore",
        ".python-version",
        ".env.example",
    ]

    for f in required_files:
        assert Path(f).is_file(), f"File {f} is missing"


def test_package_markers():
    """Verify that __init__.py markers are present."""
    assert Path("src/__init__.py").is_file()
    assert Path("tests/__init__.py").is_file()
