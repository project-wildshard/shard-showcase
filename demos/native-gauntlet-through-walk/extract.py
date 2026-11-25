import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from geometry import export
export(*map(Path,sys.argv[sys.argv.index("--")+1:]))
