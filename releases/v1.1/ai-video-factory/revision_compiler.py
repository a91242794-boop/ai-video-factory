#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--qa',required=True); ap.add_argument('--output',required=True); a=ap.parse_args()
    qa=json.loads(Path(a.qa).read_text(encoding='utf-8'))
    failures=qa.get('failures') or qa.get('issues') or []
    keep=qa.get('keep',['all correct panels','actor identity','product proportions','lighting and composition not listed as failed'])
    text='KEEP: '+ '; '.join(map(str,keep))+'.\nFIX ONLY: '+ '; '.join(map(str,failures))+'.\nDO NOT: alter correct panels, redesign packaging, add text, change actor, change scene, add new claims.\n'
    Path(a.output).write_text(text,encoding='utf-8'); print(text)
if __name__=='__main__': main()
