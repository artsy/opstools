import sys

from pathlib import Path

# add repo root to sys.path
# mostly for importing modules in 'lib' dir
path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))
