import re
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ivorybox import __version__
text = Path("pyproject.toml").read_text()
assert re.search(r'^version = "' + re.escape(__version__) + r'"$', text, re.M)
assert "## [" + __version__ + "]" in Path("CHANGELOG.md").read_text()
print("Version consistent:", __version__)
