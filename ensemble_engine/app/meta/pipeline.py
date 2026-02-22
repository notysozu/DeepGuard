from __future__ import annotations

from pathlib import Path

from ensemble_engine.app.meta.loader import MetaArtifacts



def load_meta_pipeline(base_dir: str = "ensemble_engine/artifacts") -> MetaArtifacts:
    artifacts = MetaArtifacts(Path(base_dir))
    artifacts.load()
    return artifacts
