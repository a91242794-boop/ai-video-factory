#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
import yaml

MODE_EXTRA = {
    'compact': '',
    'standard': '\nContinuity priority: preserve the exact same actor, product, room, light and color treatment across all applicable panels. Each panel must remain visually distinct and readable after vertical crop.',
    'strict': '\nHARD LOCK: do not reinterpret, redesign, stylize or relabel the product. Do not add any typography. Do not change actor identity, hair, clothing, room, time or lighting. Treat every immutable item as a non-negotiable production constraint.'
}

def load_yaml(path):
    return yaml.safe_load(Path(path).read_text(encoding='utf-8'))

def compact_list(items):
    return '; '.join(str(x).strip() for x in items if str(x).strip())

def compile_prompt(dsl, lock, mode='compact', panels=None):
    selected = dsl['shots']
    if panels:
        wanted = set(panels)
        selected = [s for s in selected if s['id'] in wanted]
    p = lock['product']; c = lock['character']; e = lock['environment']; cam = lock['cinematography']; b = lock['brand']
    lines = []
    lines.append(f"Generate a {'4-panel preview board' if panels else '4x4, 16-panel storyboard'} read left-to-right, top-to-bottom. Every panel must be independently crop-safe for {dsl['format']['crop']} vertical video.")
    lines.append("Use the uploaded product images as the only visual source of truth.")
    lines.append("LOCKS:")
    lines.append(f"PRODUCT: {compact_list(p['immutable'])}. Scale: {p['scale']}.")
    lines.append(f"CHARACTER: {compact_list(c['immutable'])}.")
    lines.append(f"ENVIRONMENT: {compact_list(e['immutable'])}.")
    lines.append(f"CAMERA: lenses {compact_list(cam.get('lens_set', []))}; motion {compact_list(cam.get('movement', []))}; {cam.get('framing','')}.")
    lines.append(f"STYLE: {compact_list(b['immutable'])}.")
    lines.append("PANELS:")
    for s in selected:
        lines.append(f"{s['id']}. [{s['shot']}] {s['visual']}; {s['action']}.")
    lines.append("LAYOUT: thin plain white gutters only; no labels or graphic UI; visually coherent commercial photography; no repeated composition.")
    lines.append("DO NOT: " + compact_list(lock['global_negative']) + ".")
    if MODE_EXTRA[mode]:
        lines.append(MODE_EXTRA[mode].strip())
    return '\n'.join(lines).strip() + '\n'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--dsl', required=True)
    ap.add_argument('--lock', required=True)
    ap.add_argument('--mode', choices=MODE_EXTRA, default='compact')
    ap.add_argument('--panels', default='')
    ap.add_argument('--output', required=True)
    ap.add_argument('--meta-output')
    args=ap.parse_args()
    dsl=load_yaml(args.dsl); lock=load_yaml(args.lock)
    panels=[int(x) for x in args.panels.split(',') if x.strip()] or None
    prompt=compile_prompt(dsl, lock, args.mode, panels)
    out=Path(args.output); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(prompt, encoding='utf-8')
    digest=hashlib.sha256((Path(args.dsl).read_text(encoding='utf-8')+Path(args.lock).read_text(encoding='utf-8')+args.mode+str(panels)).encode()).hexdigest()
    meta={'sha256':digest,'mode':args.mode,'panels':panels or 'all','characters':len(prompt),'estimated_tokens':round(len(prompt)/4)}
    if args.meta_output:
        Path(args.meta_output).write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(meta,ensure_ascii=False))
if __name__=='__main__': main()
