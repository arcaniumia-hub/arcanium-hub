export const meta = {
  name: 'silence-hyper-review',
  description: 'Two independent critics review the whole film from contact sheets, fix agents repair each flagged scene, verifiers check the fixes (up to 2 rounds)',
  phases: [
    { title: 'Critique', detail: 'craft juror + edit/tech supervisor' },
    { title: 'Fix', detail: 'one agent per flagged scene group' },
    { title: 'Verify', detail: 'adversarial check of each fix, second round if needed' },
  ],
}
const ROOT = '/home/user/arcanium-hub/video/silence-hyper'
const GROUPS = { 's01-before': 's01-s02', 's02-break': 's01-s02', 's12-handoff': 's12-s13', 's13-lumarc': 's12-s13' }
const groupOf = id => GROUPS[id] || id
const IDS_OF = g => g === 's01-s02' ? ['s01-before', 's02-break'] : g === 's12-s13' ? ['s12-handoff', 's13-lumarc'] : [g]

const CONTEXT = `Project: ${ROOT} — "SILENCE ONE — On Mute", a 34.4 s vertical (1080x1920, 30 fps, 150 BPM: beat b = b*0.4 s) product film for the studio LUMARC, rendered by a custom three.js + 2D-canvas engine. The client asked for "the most insane motion graphics in the world, with impressive editing", in the format: a cheap, tacky BEFORE presentation, a break, then the spectacular AFTER, ending with the LUMARC call-to-action card. Read ${ROOT}/storyboard.json (concept, globalStyle, scenes, cueSheet), ${ROOT}/GUIDE.md and ${ROOT}/review/build-reports.md (what each scene author built). Contact sheets of the CURRENT full build: ${ROOT}/review/overview.jpg (one frame per beat; flashes on hit frames are intended) and ${ROOT}/review/<sceneId>.jpg (each labelled with time + beat, 0.1 s steps; 0.2 s for s01 and s13). Scene ids: s01-before s02-break s03-this s04-reveal s05-grid s06-noise s07-mute s08-gyro s09-gates s10-bloom s11-hero s12-handoff s13-lumarc. You may render extra full-res frames of the full film with: cd ${ROOT} && NODE_PATH=/opt/node-tools/node_modules node tools/render.cjs stills review/extra_<yourname> <t1> <t2> ... (index.html/bundle.js is the current full build; do NOT rebuild it). Rendering is slow (~2 s/frame, 2 agents share 4 CPUs): be selective.`

const ISSUES = {
  type: 'object',
  properties: {
    overall: { type: 'string' },
    topPriorities: { type: 'array', items: { type: 'string' } },
    issues: { type: 'array', items: { type: 'object', properties: {
      scene: { type: 'string', description: 'scene id' }, severity: { type: 'string', enum: ['critical', 'major', 'minor'] },
      timeSec: { type: 'string' }, problem: { type: 'string' }, fix: { type: 'string', description: 'concrete, implementable fix' } },
      required: ['scene', 'severity', 'timeSec', 'problem', 'fix'] } },
  },
  required: ['overall', 'topPriorities', 'issues'],
}
const LENSES = [
  { key: 'craft', text: 'You are a Cannes Lions / Motion Awards craft juror and the creative director of a top motion studio (ManvsMachine, Buck, Apple product films). Judge every scene for world-class craft: composition and use of the 9:16 frame, typography (hierarchy, size on a phone, kerning, font pairing), lighting and materials of the 3D product (does it look premium and like the same product everywhere?), motion design (curves, anticipation, follow-through, secondary motion), originality, and whether each scene delivers its signature moment from the storyboard. Call out anything that looks cheap, generic, muddy, empty, over-busy, blown out, or template-like (except the intentionally cheap BEFORE, which must be convincingly tacky but cleanly rendered). Prioritise the issues that most hurt the "insane, world-class" impression.' },
  { key: 'edit', text: 'You are the editor and technical supervisor. Check: continuity at every scene boundary (compare the last frames of each scene with the first frames of the next — do the object-match cuts in the storyboard actually line up in position/scale/colour?), beat sync of cuts and hits against the cueSheet, consistency of the ANC ring motif and of the palette/type system across scenes, phone legibility (copy inside x 80-1000, y 220-1640, no text < 30 px, text on screen long enough to read), the LUMARC end card (correct logo/copy/colours, readable, holds >= 2.5 s), and technical artifacts (black or empty frames, popping, flicker, aliasing, banding, clipped text, broken layering, wrong colours, elements that vanish between frames). Be precise about times.' },
]

phase('Critique')
const crits = (await parallel(LENSES.map(l => () => agent(
  `${CONTEXT}\n\n${l.text}\n\nLook at EVERY review sheet (Read the images). Report every real issue with scene id, severity (critical = breaks the film or looks broken/cheap in a hero moment; major = clearly below world-class; minor = polish), the time, the problem and a concrete fix the scene's programmer can implement. Do not report things that match the storyboard intent unless they look bad. Do not edit any files.`,
  { label: `critic:${l.key}`, phase: 'Critique', schema: ISSUES, effort: 'high' })))).filter(Boolean)

const all = crits.flatMap((c, i) => c.issues.map(x => ({ ...x, by: LENSES[i].key })))
// engine/timing/motion-blur/fg-upload bugs were already fixed by the integrator in engine.js/main.js -> drop them;
// issues naming several scenes are copied to each named scene's group
const SCENE_IDS = ['s01-before', 's02-break', 's03-this', 's04-reveal', 's05-grid', 's06-noise', 's07-mute', 's08-gyro', 's09-gates', 's10-bloom', 's11-hero', 's12-handoff', 's13-lumarc']
const ENGINE = /engine\.js|main\.js|lib\.js timing|FG upload|motion blur\)/
const groups = {}
for (const x of all) {
  if (ENGINE.test(x.scene)) continue
  const nums = [...new Set((x.scene.match(/s(\d\d)/g) || []).map(m => m.slice(1)))]
  const ids = nums.map(n => SCENE_IDS.find(id => id.startsWith('s' + n))).filter(Boolean)
  for (const id of ids) { const g = groupOf(id); if (!groups[g]) groups[g] = []; groups[g].push({ ...x, scene: ids.length > 1 ? id + ' (shared issue: ' + x.scene + ')' : id }) }
}
const toFix = Object.keys(groups).filter(g => groups[g].some(x => x.severity !== 'minor') || groups[g].length >= 3)
log(`${all.length} issues; fixing ${toFix.length} scene groups: ${toFix.join(', ')}`)
const fmt = list => list.map((x, i) => `${i + 1}. [${x.severity}] ${x.scene} @ ${x.timeSec} (${x.by}): ${x.problem}\n   FIX: ${x.fix}`).join('\n')
const priorities = crits.map((c, i) => `${LENSES[i].key}: ${c.overall}\nTop: ${c.topPriorities.join(' | ')}`).join('\n\n')

const VERDICT = { type: 'object', properties: {
  unresolved: { type: 'array', items: { type: 'object', properties: { problem: { type: 'string' }, fix: { type: 'string' }, severity: { type: 'string', enum: ['critical', 'major', 'minor'] } }, required: ['problem', 'fix', 'severity'] } },
  regressions: { type: 'array', items: { type: 'string' } }, notes: { type: 'string' } }, required: ['unresolved', 'regressions', 'notes'] }

const fixPrompt = (g, list, round) => `${CONTEXT}\n\nYou are the motion designer / creative coder who owns ${IDS_OF(g).map(id => `src/scenes/${id}.js`).join(' and ')}. Two senior reviewers watched the whole film. Their overall verdicts:\n${priorities}\n\nIssues for YOUR scene(s)${round > 1 ? ' that a verifier found still unresolved after the first fix round' : ''}:\n${fmt(list)}\n\nNOTE: the integrator already fixed three engine bugs (motion-blur sub-frames darkened the image, a stale foreground layer could leak the previous scene's 2D content, and float error put downbeat frames one frame late) — do not compensate for them in your scene, and remove any brightness compensation for motion blur you find in your file. Fix every critical and major issue and every minor one that is cheap, raising the scene to world-class. Read GUIDE.md's rules. Build and render ONLY your scene: node tools/build.cjs <id>; PAGE=tmp/<id>/index.html node tools/render.cjs sheet|stills ... (export NODE_PATH=/opt/node-tools/node_modules). Read every image you render. For boundary issues compare your first/last frames with the neighbouring scene's sheet in review/. Edit only your own scene file(s); never touch engine/lib/model/fx3d/main/index/GUIDE/storyboard or other scenes; never rebuild the full film. Keep frame render time <= ~2.5 s. Return what you changed per issue, anything you could not fix and why.`

const verifyPrompt = (g, list) => `${CONTEXT}\n\nYou are an adversarial verifier. The owner of ${IDS_OF(g).join(' + ')} just claims to have fixed these issues:\n${fmt(list)}\n\nBuild and render the scene(s) yourself (node tools/build.cjs <id>; PAGE=tmp/<id>/index.html node tools/render.cjs sheet tmp/<id>/verify.jpg <from> <to> 0.1 6, plus stills of the specific times; export NODE_PATH=/opt/node-tools/node_modules) and look hard. Default to "unresolved" when in doubt. Also report regressions (anything that got worse or broke). Do not edit scene files.`

phase('Fix')
const results = await pipeline(toFix,
  g => agent(fixPrompt(g, groups[g], 1), { label: `fix:${g}`, phase: 'Fix', effort: 'high' }).then(r => ({ g, fix1: r })),
  r => agent(verifyPrompt(r.g, groups[r.g]), { label: `verify:${r.g}`, phase: 'Verify', schema: VERDICT }).then(v => ({ ...r, v1: v })),
  r => {
    const left = r.v1.unresolved.filter(x => x.severity !== 'minor')
    if (!left.length && !r.v1.regressions.length) return r
    const list = [...left.map(x => ({ ...x, scene: r.g, timeSec: '-', by: 'verifier' })), ...r.v1.regressions.map(x => ({ severity: 'major', scene: r.g, timeSec: '-', problem: 'REGRESSION: ' + x, fix: 'restore/repair', by: 'verifier' }))]
    return agent(fixPrompt(r.g, list, 2), { label: `fix2:${r.g}`, phase: 'Fix', effort: 'high' }).then(f => ({ ...r, fix2: f, left2: list }))
  })
return { critics: crits.map((c, i) => ({ lens: LENSES[i].key, overall: c.overall, topPriorities: c.topPriorities, nIssues: c.issues.length })),
  groupsFixed: toFix, minorOnly: Object.keys(groups).filter(g => !toFix.includes(g)).map(g => ({ g, issues: groups[g] })),
  results: results.filter(Boolean).map(r => ({ g: r.g, fix1: r.fix1, unresolvedAfter1: r.v1 && r.v1.unresolved, regressions: r.v1 && r.v1.regressions, fix2: r.fix2 || null })) }
