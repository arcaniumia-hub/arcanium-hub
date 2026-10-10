#!/bin/bash
# Full-film review sheets: one contact sheet per scene (0.1 s steps; 0.2 s for long calm scenes) + a 0.4 s overview.
#   tools/review.sh [sceneId ...]   (default: all scenes)   -> review/<id>.jpg, review/overview.jpg
set -e; cd "$(dirname "$0")/.."; export NODE_PATH=/opt/node-tools/node_modules
node tools/build.cjs >/dev/null
mkdir -p review
node tools/render.cjs info 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin); want=sys.argv[1:]
for s in d['scenes']:
  if want and s['id'] not in want: continue
  dur=s['t1']-s['t0']; step=0.1 if dur<=3.3 else 0.2
  print(s['id'], round(s['t0'],3), round(s['t1']-0.0334,3), step)
" "$@" > review/plan.txt
run() { while read id a b st; do node tools/render.cjs sheet review/$id.jpg $a $b $st 6 2>&1 | grep -E 'PAGEERR|\[sheet\]' | sed "s/^/$id /"; done; }
# two renderers in parallel (4 CPUs)
awk 'NR%2==1' review/plan.txt | run & awk 'NR%2==0' review/plan.txt | run & wait
if [ $# -eq 0 ]; then node tools/render.cjs sheet review/overview.jpg 0 34.0 0.4 12 2>&1 | grep -E 'PAGEERR|\[sheet\]'; fi
echo review-done
