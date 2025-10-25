"""
EADA Pro - Quick Run Script
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path so `import src` works regardless of CWD
PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.main import main

if __name__ == "__main__":
    sys.exit(main())
