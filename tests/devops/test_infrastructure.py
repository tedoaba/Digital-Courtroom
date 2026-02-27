import os


def test_infrastructure_files_exist():
    """Verify essential DevOps files exist in root."""
    assert os.path.exists("Makefile")
    assert os.path.exists(".dockerignore")
    assert os.path.exists(".hadolint.yaml")
    # Dockerfile will be created in US2, but for TDD Red Phase we can assert it exists
    # assert os.path.exists("Dockerfile")


def test_makefile_targets():
    """Verify Makefile has all required public targets."""
    with open("Makefile") as f:
        content = f.read()

    required_targets = [
        "run:",
        "cli:",
        "test:",
        "lint:",
        "docker-build:",
        "docker-run:",
        "clean:",
        ".check-uv:",
        ".check-env:",
        ".check-dirs:",
    ]

    for target in required_targets:
        assert target in content, f"Target {target} missing from Makefile"


def test_preflight_checks():
    """Placeholder for checking pre-flight logic."""
    # This will be tested by running make targets and checking return codes
    pass
