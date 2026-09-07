import sys
from pathlib import Path

tests_dir = Path(__file__).parent
backend_dir = tests_dir.parent

if str(tests_dir) not in sys.path:
    sys.path.insert(0, str(tests_dir))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
