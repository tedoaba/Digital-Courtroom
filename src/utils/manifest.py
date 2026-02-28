"""
Manifest Manager for Digital Courtroom runs.
Handles serialization of run_manifest.json per Constitution XVII.2.
"""

import json
import os
from datetime import UTC, datetime
from typing import Any


class ManifestManager:
    """Manages the creation and storage of the run manifest."""

    @staticmethod
    def save_manifest(
        output_dir: str,
        state_metadata: dict[str, Any],
        errors: list[str],
    ) -> str:
        """
        Saves the manifest to the specified directory.
        Returns the path to the saved file.
        """
        manifest = {
            "timestamp": datetime.now(UTC).isoformat(),
            "status": state_metadata.get("run_status", "SUCCESS"),
            "execution_rules": {
                "strict_layer_sync": True,
                "timeout_per_layer": 120,
                "max_re_eval_cycles": 1,
            },
            "data_trace": state_metadata,
            "errors": errors,
        }

        os.makedirs(output_dir, exist_ok=True)
        manifest_path = os.path.join(output_dir, "run_manifest.json")

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return manifest_path
