from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arm_guard.runtime import ArmGuardApplication


if __name__ == "__main__":
    app = ArmGuardApplication.build_default()
    print(json.dumps(app.run_benchmark(iterations=100), indent=2))
