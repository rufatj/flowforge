"""FlowForge backend application package.

The backend reuses the eval package (n8n client, gates, JSON extraction)
rather than duplicating that logic. `eval` lives at the repo root locally
(flowforge/eval next to flowforge/backend) and next to app/ inside the
Docker image, so we walk upward until we find it.
"""
import sys
from pathlib import Path

for _parent in Path(__file__).resolve().parents:
    if (_parent / "eval" / "harness.py").exists():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

__version__ = "0.2.0"
