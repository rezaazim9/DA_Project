"""One-command offline reproduction after installing requirements.txt."""
from pathlib import Path
import argparse
import subprocess
import sys

ROOT=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-pdf",action="store_true",help="Reproduce analysis/notebook/tests without a TeX installation")
    parser.add_argument("--download",action="store_true",help="Download missing pinned input files")
    args=parser.parse_args()
    steps=[]
    if args.download:steps.append([sys.executable,"-m","src.download"])
    steps += [[sys.executable,"-m","src.audit"],[sys.executable,"-m","src.build_notebook"],[sys.executable,"-m","unittest","discover","-s","tests","-v"]]
    if not args.skip_pdf:steps.append([sys.executable,"-m","src.build_documents"])
    for step in steps:
        print("Running:"," ".join(step),flush=True)
        subprocess.run(step,cwd=ROOT,check=True)
    print("Reproduction completed.")


if __name__=="__main__":main()
