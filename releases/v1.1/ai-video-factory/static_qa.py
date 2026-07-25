#!/usr/bin/env python3
import argparse, json, re
from pathlib import Path
import yaml

def load(path): return yaml.safe_load(Path(path).read_text(encoding='utf-8'))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--dsl',required=True); ap.add_argument('--brief',required=True); ap.add_argument('--output',required=True); a=ap.parse_args()
    dsl=load(a.dsl); brief=load(a.brief); shots=dsl.get('shots',[])
    issues=[]; score=100
    if len(shots)!=dsl.get('format',{}).get('panels',16): issues.append('shot_count_mismatch'); score-=25
    ids=[s.get('id') for s in shots]
    if ids!=list(range(1,len(shots)+1)): issues.append('non_sequential_ids'); score-=10
    reveal=min([s['id'] for s in shots if s.get('purpose') in ('reveal','product_reveal')], default=99)
    if reveal>5: issues.append('product_appears_too_late'); score-=10
    visuals=[str(s.get('visual','')).strip().lower() for s in shots]
    if len(set(visuals))<len(visuals): issues.append('duplicate_visuals'); score-=10
    forbidden=[]
    for x in brief.get('message',{}).get('prohibited_claims',[]): forbidden.extend(re.findall(r'[a-zA-Z]+',str(x).lower()))
    joined=' '.join(visuals+[str(s.get('action','')).lower() for s in shots])
    hits=sorted({w for w in forbidden if len(w)>4 and w in joined})
    if hits: issues.append({'prohibited_claim_terms':hits}); score-=20
    required={'hook','reveal','apply','use','hero','cta_plate'}
    purposes={s.get('purpose') for s in shots}
    missing=sorted(required-purposes)
    if missing: issues.append({'missing_purposes':missing}); score-=5*len(missing)
    report={'score':max(score,0),'pass':score>=90 and not any(i=='shot_count_mismatch' for i in issues),'issues':issues,'model_tokens_used':0}
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__': main()
