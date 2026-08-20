import shutil
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / 'hris_preview_submission.zip'

if OUT.exists():
    OUT.unlink()

shutil.make_archive(str(OUT).replace('.zip',''), 'zip', root_dir=ROOT)
print('Created', OUT)
