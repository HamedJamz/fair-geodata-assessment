#!/usr/bin/env python3
"""Run the whole workflow: harvest -> assess -> analyse.  (F-UJI step is optional:
run scripts/03_run_fuji.py before step 4 if a local F-UJI server is available.)"""
import subprocess, sys
from pathlib import Path

here = Path(__file__).resolve().parent
for step in ("01_harvest_datacite.py", "02_assess_metadata.py", "04_analyse.py"):
    print(f"\n===== {step} =====", flush=True)
    subprocess.run([sys.executable, str(here / "scripts" / step), *sys.argv[1:]] if step.startswith("01")
                   else [sys.executable, str(here / "scripts" / step)], check=True)
