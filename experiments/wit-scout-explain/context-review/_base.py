"""Use the existing versioned Scout code, without copying or replacing it."""
from pathlib import Path
import sys

BASE_DIRECTORY = (Path(__file__).resolve().parents[3] /
                  "tools/scout-explain/0.1.0-public-draft.1")
BASE_COMMIT = "a2789ef29a7a34b7709c01beb5d92600cb1f35c6"
if not (BASE_DIRECTORY / "research_checkpoint.py").is_file():
    raise RuntimeError("Keep this experiment in its WIT repository checkout")

# These modules use sibling imports. Refuse a conflicting module already loaded
# by the embedding process, rather than silently mixing different Scout builds.
for name in ("scout", "provider_adapter", "evidence_gate", "claim_review",
             "semantic_guard", "research_handoff", "trusted_host_bridge",
             "github_connector_adapter", "research_checkpoint"):
    module = sys.modules.get(name)
    if module is not None and Path(getattr(module, "__file__", "")).resolve() != (
            BASE_DIRECTORY / (name + ".py")):
        raise RuntimeError("A different Scout module is already loaded")
sys.path[:] = [entry for entry in sys.path if entry != str(BASE_DIRECTORY)]
sys.path.insert(0, str(BASE_DIRECTORY))

from research_checkpoint import (  # noqa: E402
    ResearchSession, SCHEMA, MAX_CHECKPOINT_BYTES, _decode, _restore, load_research_checkpoint,
    save_research_checkpoint,
)
from research_handoff import build_handoff  # noqa: E402
from trusted_host_bridge import Gathered, HostRead, gather  # noqa: E402
from scout import canonical_url  # noqa: E402

for name in ("scout", "provider_adapter", "evidence_gate", "claim_review",
             "semantic_guard", "research_handoff", "trusted_host_bridge",
             "github_connector_adapter", "research_checkpoint"):
    if Path(sys.modules[name].__file__).resolve() != BASE_DIRECTORY / (name + ".py"):
        raise RuntimeError("Scout imports must resolve to the versioned source")
