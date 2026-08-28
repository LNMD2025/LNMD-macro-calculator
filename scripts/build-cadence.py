#!/usr/bin/env python3
"""Build the Cadence PWA from the live cdncapp.com snapshot."""
from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path("/workspace")
SRC = Path("/tmp/cadence-live/cadence.html")


def write_png(path: Path, size: int, rgba_fn) -> None:
    raw = bytearray()
    for y in range(size):
        raw.append(0)
        for x in range(size):
            raw.extend(rgba_fn(x, y, size))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def cadence_icon(x: int, y: int, size: int) -> bytes:
    cx = cy = size / 2
    r = size * 0.42
    dx, dy = x - cx, y - cy
    dist = (dx * dx + dy * dy) ** 0.5
    # charcoal background
    bg = (18, 17, 16, 255)
    orange = (217, 79, 30, 255)
    white = (247, 246, 243, 255)
    if dist > r + size * 0.04:
        return bytes(bg)
    if abs(dist - r) < size * 0.055:
        return bytes(orange)
    # checkmark
    # line 1: from 0.32,0.50 to 0.45,0.64
    # line 2: from 0.45,0.64 to 0.70,0.36
    def near_seg(x0, y0, x1, y1, thickness):
        px, py = x / size, y / size
        vx, vy = x1 - x0, y1 - y0
        lx = px - x0
        ly = py - y0
        den = vx * vx + vy * vy
        t = 0 if den == 0 else max(0, min(1, (lx * vx + ly * vy) / den))
        nx, ny = x0 + t * vx, y0 + t * vy
        return ((px - nx) ** 2 + (py - ny) ** 2) ** 0.5 < thickness

    if near_seg(0.30, 0.50, 0.44, 0.66, 0.045) or near_seg(0.44, 0.66, 0.72, 0.34, 0.045):
        return bytes(orange)
    return bytes(bg)


FREE_VIEW = r'''
    <!-- FREE TOOLS / MACRO CALCULATOR -->
    <section class="view" id="view-free">
      <div class="view-header"><h2>Free Tools</h2></div>
      <div class="free-wrap">
        <p class="free-lead">Science-backed daily macros. Runs on your phone, works offline after install.</p>
        <form id="macroForm" class="macro-form" novalidate>
          <div class="macro-grid">
            <label>Wake time
              <select id="wakeTime" required></select>
            </label>
            <label>Sleep time
              <select id="sleepTime" required></select>
            </label>
            <label>Weight (kg)
              <input id="weight" type="number" inputmode="decimal" min="30" max="250" step="0.1" required>
            </label>
            <label>Body fat (%)
              <input id="bodyFat" type="number" inputmode="decimal" min="3" max="60" step="0.1" required>
            </label>
            <label>Daily steps
              <input id="steps" type="number" inputmode="numeric" min="1000" max="40000" step="100" value="8000" required>
            </label>
            <label>Sessions / day
              <select id="sessionsPerDay">
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
              </select>
            </label>
          </div>
          <div id="sessionTimes" class="macro-grid"></div>
          <fieldset class="macro-train">
            <legend>Weekly training</legend>
            <div id="trainingTypes"></div>
            <button type="button" class="btn btn-ghost" id="addTrainingBtn">+ Add training type</button>
          </fieldset>
          <div class="macro-grid">
            <label>Goal
              <select id="macroGoal">
                <option value="maintain">Maintain</option>
                <option value="recomp">Recomp (−5%)</option>
                <option value="moderateCut">Moderate loss (−15%)</option>
                <option value="aggressiveCut">Aggressive loss (−30%)</option>
                <option value="aggressiveBulk">Aggressive gain (+20%)</option>
                <option value="performance">Performance (+10%)</option>
              </select>
            </label>
            <label>Protein (g/kg total)
              <select id="proteinLevel">
                <option value="1.5">Moderate 1.5</option>
                <option value="0.8">Low 0.8</option>
                <option value="2.2" selected>High 2.2</option>
              </select>
            </label>
            <label>Fat (g/kg lean)
              <select id="fatLevel">
                <option value="1.4" selected>Moderate 1.4</option>
                <option value="0.8">Low 0.8</option>
                <option value="2.0">High 2.0</option>
              </select>
            </label>
          </div>
          <p class="macro-error" id="macroError" hidden></p>
          <button type="submit" class="btn btn-primary btn-block" id="macroSubmit">Calculate</button>
        </form>
        <div id="macroResults" class="macro-results" hidden>
          <div class="macro-totals">
            <div><b id="outKcal"></b><span>kcal</span></div>
            <div><b id="outP"></b><span>protein</span></div>
            <div><b id="outC"></b><span>carbs</span></div>
            <div><b id="outF"></b><span>fat</span></div>
          </div>
          <details class="macro-breakdown"><summary>How this was calculated</summary><div id="macroBreakdown"></div></details>
          <h3>Daily timeline</h3>
          <ul id="macroTimeline" class="macro-timeline"></ul>
          <button type="button" class="btn btn-ghost btn-block" id="saveMacroBtn">Save to my Cadence profile</button>
        </div>
      </div>
    </section>
'''

FREE_CSS = r'''
/* ===== PWA / MOBILE HARDENING ===== */
html{padding:env(safe-area-inset-top) env(safe-area-inset-right) 0 env(safe-area-inset-left)}
.mobile-topbar{padding-top:calc(12px + env(safe-area-inset-top))}
.bottom-tabbar{padding-bottom:calc(8px + env(safe-area-inset-bottom))}
#mobileMoreFab{bottom:calc(78px + env(safe-area-inset-bottom))}
@media(min-width:640px){#mobileMoreFab{display:none !important}}
input,select,textarea{font-size:16px}
.install-banner{display:none;align-items:center;gap:12px;margin:12px 16px;padding:12px 14px;border:1px solid var(--color-border);border-radius:var(--radius-lg);background:var(--color-surface);box-shadow:var(--shadow-sm)}
.install-banner.show{display:flex}
.install-banner p{flex:1;font-size:.85rem}
.install-banner strong{display:block}
.auth-gate{position:fixed;inset:0;z-index:200;background:var(--color-bg);display:flex;align-items:center;justify-content:center;padding:24px}
.auth-gate.hidden{display:none}
.auth-card{width:100%;max-width:400px;background:var(--color-surface);border:1px solid var(--color-border);border-radius:var(--radius-xl);padding:28px 22px;box-shadow:var(--shadow-lg)}
.auth-brand{display:flex;align-items:center;gap:10px;font-family:var(--font-display);font-weight:800;font-size:1.4rem;margin-bottom:18px}
.auth-tabs{display:flex;gap:8px;margin-bottom:16px}
.auth-tabs button{flex:1;padding:10px;border-radius:var(--radius-md);font-weight:700;background:var(--color-surface-offset)}
.auth-tabs button.active{background:var(--color-primary);color:#fff}
.auth-field{margin-bottom:12px}
.auth-field label{display:block;font-size:.78rem;font-weight:700;margin-bottom:6px;color:var(--color-text-muted);text-transform:uppercase}
.auth-field input{width:100%;padding:12px;border:1px solid var(--color-border);border-radius:var(--radius-md);background:var(--color-surface-2)}
.auth-error{color:var(--color-error);font-size:.82rem;min-height:1.2em;margin-bottom:8px}
.cd-toast{position:fixed;left:50%;bottom:calc(88px + env(safe-area-inset-bottom));transform:translateX(-50%) translateY(20px);background:var(--color-text);color:var(--color-text-inverse);padding:10px 16px;border-radius:var(--radius-full);font-size:.82rem;font-weight:600;opacity:0;pointer-events:none;z-index:300;transition:160ms}
.cd-toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
.cd-toast.error{background:var(--color-error);color:#fff}
.signout-row{display:flex;align-items:center;gap:14px;padding:12px;border-radius:var(--radius-lg);color:var(--color-text-muted)}
.free-wrap{padding:8px 16px 32px;max-width:560px}
.free-lead{color:var(--color-text-muted);font-size:.9rem;margin-bottom:16px}
.macro-form label{display:flex;flex-direction:column;gap:6px;font-size:.78rem;font-weight:700;color:var(--color-text-muted);text-transform:uppercase;letter-spacing:.03em}
.macro-form input,.macro-form select{padding:12px;border:1px solid var(--color-border);border-radius:var(--radius-md);background:var(--color-surface-2);font-weight:500;text-transform:none;letter-spacing:0;color:var(--color-text)}
.macro-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px}
@media(max-width:420px){.macro-grid{grid-template-columns:1fr}}
.macro-train{border:1px solid var(--color-border);border-radius:var(--radius-lg);padding:12px;margin-bottom:14px}
.macro-train legend{padding:0 6px;font-weight:700;font-size:.8rem}
.train-row{display:flex;gap:8px;margin-bottom:8px}
.train-row select{flex:2}
.train-row input{flex:1;min-width:0}
.macro-error{color:var(--color-error);font-size:.85rem;margin-bottom:10px}
.macro-results{margin-top:20px}
.macro-totals{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:16px}
.macro-totals div{background:var(--color-surface);border:1px solid var(--color-border);border-radius:var(--radius-lg);padding:12px 8px;text-align:center}
.macro-totals b{display:block;font-family:var(--font-display);font-size:1.15rem}
.macro-totals span{font-size:.7rem;color:var(--color-text-muted);text-transform:uppercase}
.macro-timeline{list-style:none;display:flex;flex-direction:column;gap:8px;margin:10px 0 16px}
.macro-timeline li{background:var(--color-surface);border:1px solid var(--color-border);border-radius:var(--radius-md);padding:10px 12px;font-size:.85rem}
.macro-breakdown{margin-bottom:16px;color:var(--color-text-muted);font-size:.85rem}
'''

FREE_JS = r'''
/* ---------------- FREE MACRO CALCULATOR ---------------- */
const TRAIN_OPTS = [
  [0,'Select type'],[3,'Yoga/Pilates'],[4.5,'Weights'],[7,'Cycling'],[8,'Swim'],[9,'Run'],[10,'HIIT/CrossFit']
];
function fillHours(sel){
  sel.innerHTML = '<option value="">Hour</option>' + Array.from({length:24},(_,i)=>`<option value="${i}">${String(i).padStart(2,'0')}:00</option>`).join('');
}
function addTrainRow(hours=''){
  const wrap = document.getElementById('trainingTypes');
  if(!wrap) return;
  const row = document.createElement('div');
  row.className = 'train-row';
  row.innerHTML = `<select class="trainingType">${TRAIN_OPTS.map(([v,l])=>`<option value="${v}">${l}${v?` (MET ${v})`:''}</option>`).join('')}</select>
    <input class="trainingHours" type="number" inputmode="decimal" min="0" max="40" step="0.5" placeholder="hrs/wk" value="${hours}">`;
  wrap.appendChild(row);
}
function updateSessionTimes(){
  const n = parseInt(document.getElementById('sessionsPerDay').value,10) || 1;
  const box = document.getElementById('sessionTimes');
  if(!box) return;
  box.innerHTML = '';
  for(let i=1;i<=n;i++){
    const lab = document.createElement('label');
    lab.innerHTML = `Session ${i} start<select id="sessionTime${i}"></select>`;
    box.appendChild(lab);
    fillHours(lab.querySelector('select'));
  }
}
function formatHour(h){
  const hour = ((h%24)+24)%24;
  const ampm = hour>=12?'pm':'am';
  const display = hour%12 || 12;
  return display + ampm;
}
function initMacroCalculator(){
  const wake = document.getElementById('wakeTime');
  const sleep = document.getElementById('sleepTime');
  if(!wake || wake.options.length>1) return;
  fillHours(wake); fillHours(sleep);
  wake.value = '6'; sleep.value = '22';
  addTrainRow();
  updateSessionTimes();
  const sess = document.getElementById('sessionsPerDay');
  if(sess) sess.addEventListener('change', updateSessionTimes);
  const addBtn = document.getElementById('addTrainingBtn');
  if(addBtn) addBtn.addEventListener('click', ()=>addTrainRow());
  const form = document.getElementById('macroForm');
  if(form) form.addEventListener('submit', (e)=>{ e.preventDefault(); runMacroCalc(); });
  const saveBtn = document.getElementById('saveMacroBtn');
  if(saveBtn) saveBtn.addEventListener('click', saveMacroProfile);
}
function runMacroCalc(){
  const err = document.getElementById('macroError');
  err.hidden = true;
  const wakeTime = parseInt(document.getElementById('wakeTime').value,10);
  const sleepTime = parseInt(document.getElementById('sleepTime').value,10);
  const weight = parseFloat(document.getElementById('weight').value);
  const bodyFat = parseFloat(document.getElementById('bodyFat').value);
  const steps = parseFloat(document.getElementById('steps').value);
  const goal = document.getElementById('macroGoal').value;
  const proteinPerKg = parseFloat(document.getElementById('proteinLevel').value);
  const fatPerKg = parseFloat(document.getElementById('fatLevel').value);
  const sessionsPerDay = parseInt(document.getElementById('sessionsPerDay').value,10) || 1;
  const problems = [];
  if(Number.isNaN(wakeTime) || Number.isNaN(sleepTime)) problems.push('Pick wake and sleep times.');
  if(!(weight>=30 && weight<=250)) problems.push('Weight must be 30–250 kg.');
  if(!(bodyFat>=3 && bodyFat<=60)) problems.push('Body fat must be 3–60%.');
  if(!(steps>=1000 && steps<=40000)) problems.push('Steps must be 1,000–40,000.');
  const training = [];
  document.querySelectorAll('#trainingTypes .train-row').forEach(row=>{
    const met = parseFloat(row.querySelector('.trainingType').value)||0;
    const hours = parseFloat(row.querySelector('.trainingHours').value)||0;
    if(met>0 && hours>0) training.push({met,hours});
  });
  const totalHours = training.reduce((s,t)=>s+t.hours,0);
  if(totalHours<1 || totalHours>40) problems.push('Add 1–40 weekly training hours.');
  if(problems.length){ err.textContent = problems.join(' '); err.hidden=false; return; }
  const sessionTimes = [];
  for(let i=1;i<=sessionsPerDay;i++){
    const v = parseInt(document.getElementById('sessionTime'+i).value,10);
    sessionTimes.push(Number.isNaN(v) ? 8+(i-1)*4 : v);
  }
  const lean = weight * (1 - bodyFat/100);
  const bmr = 370 + 21.6 * lean;
  const baseTdee = bmr * 1.2;
  const stepsCal = 3.5 * weight * (steps / 6000);
  const exerciseCal = training.reduce((s,t)=>s + t.met * weight * (t.hours/7), 0);
  const tdee = baseTdee + stepsCal + exerciseCal;
  const adj = {aggressiveCut:0.7, moderateCut:0.85, recomp:0.95, aggressiveBulk:1.2, performance:1.1, maintain:1}[goal] || 1;
  const calories = tdee * adj;
  const protein = Math.round(weight * proteinPerKg);
  const fat = Math.round(lean * fatPerKg);
  const carbCal = calories - protein*4 - fat*9;
  const carbs = Math.round(carbCal/4);
  if(carbs < 0){
    err.textContent = 'Carbs went negative. Lower protein/fat or raise activity so calories can cover them.';
    err.hidden = false;
  }
  document.getElementById('outKcal').textContent = Math.round(calories);
  document.getElementById('outP').textContent = protein+'g';
  document.getElementById('outC').textContent = carbs+'g';
  document.getElementById('outF').textContent = fat+'g';
  document.getElementById('macroBreakdown').innerHTML =
    `Lean mass ${Math.round(lean)} kg · BMR ${Math.round(bmr)} · TDEE ${Math.round(tdee)} · Goal ${goal} (${Math.round((adj-1)*100)}%). Protein uses total weight; fat uses lean mass; carbs fill remaining calories.`;
  let wCarb=0.5,wPro=0.5,wFat=0.3;
  if(goal==='performance'||goal==='aggressiveBulk'){ wCarb=0.7; wPro=0.4; wFat=0.2; }
  else if(goal==='aggressiveCut'||goal==='recomp'){ wCarb=0.4; wPro=0.6; wFat=0.4; }
  const events = [];
  sessionTimes.forEach((start, idx)=>{
    const n = idx+1;
    const specs = [
      {hour:(start-1+24)%24, label:`${formatHour(start-1)} · Pre ${n}`, p:0.3,c:0.3,f:0.4},
      {hour:start, label:`${formatHour(start)} · Intra ${n}`, p:0.2,c:0.3,f:0.2},
      {hour:(start+1)%24, label:`${formatHour(start+1)} · Post ${n}`, p:0.5,c:0.4,f:0.4}
    ];
    specs.forEach(s=>events.push({
      hour:s.hour, label:s.label,
      protein: Math.round(protein * (wPro/sessionsPerDay) * s.p),
      carbs: Math.round(carbs * (wCarb/sessionsPerDay) * s.c),
      fats: Math.round(fat * (wFat/sessionsPerDay) * s.f)
    }));
  });
  const otherP = Math.round(protein * (1-wPro) / 3);
  const otherC = Math.round(carbs * (1-wCarb) / 3);
  const otherF = Math.round(fat * (1-wFat) / 3);
  const awake = sleepTime>wakeTime ? sleepTime-wakeTime : sleepTime-wakeTime+24;
  let t = wakeTime;
  for(let i=0;i<3;i++){
    t += awake/4;
    let hour = Math.floor(t)%24;
    while(events.some(e=>e.hour===hour)) { t+=1; hour=Math.floor(t)%24; }
    events.push({hour, label:`${formatHour(hour)} · Meal ${i+1}`, protein:otherP, carbs:otherC, fats:otherF});
  }
  events.sort((a,b)=>a.hour-b.hour);
  document.getElementById('macroTimeline').innerHTML = events.map(e=>
    `<li><strong>${e.label}</strong><div>P ${e.protein}g · C ${e.carbs}g · F ${e.fats}g</div></li>`
  ).join('');
  document.getElementById('macroResults').hidden = false;
  window._lastMacro = {
    label: `${goal} @ ${new Date().toISOString().slice(0,10)}`,
    calories: Math.round(calories), protein_g: protein, carbs_g: carbs, fat_g: fat,
    bodyweight_kg: weight, goal, diet: null, activity: totalHours+'h/wk',
    bmr: Math.round(bmr), tdee: Math.round(tdee),
    inputs: {wakeTime,sleepTime,bodyFat,steps,sessionsPerDay,sessionTimes,training,proteinPerKg,fatPerKg}
  };
}
async function saveMacroProfile(){
  if(!window._lastMacro){ showToast('Calculate first', true); return; }
  if(!state.user){ showToast('Sign in to save', true); return; }
  try{
    const row = Object.assign({}, window._lastMacro, {
      user_id: state.user.id,
      auth_user_id: state.user.id
    });
    const { error } = await sb.from('macro_profiles').insert(row);
    if(error) throw error;
    showToast('Saved to your profile');
  }catch(err){
    console.error('[saveMacro]', err);
    showToast('Could not save macros', true);
  }
}
'''

PWA_JS = r'''
/* ---------------- PWA INSTALL + SERVICE WORKER ---------------- */
if('serviceWorker' in navigator){
  window.addEventListener('load', ()=>{
    navigator.serviceWorker.register('./sw.js').catch(err=>console.warn('[sw]', err));
  });
}
let deferredPrompt = null;
window.addEventListener('beforeinstallprompt', (e)=>{
  e.preventDefault();
  deferredPrompt = e;
  const ban = document.getElementById('installBanner');
  if(ban && !window.matchMedia('(display-mode: standalone)').matches) ban.classList.add('show');
});
document.addEventListener('click', async (e)=>{
  if(e.target && e.target.id === 'installAppBtn' && deferredPrompt){
    deferredPrompt.prompt();
    await deferredPrompt.userChoice;
    deferredPrompt = null;
    const ban = document.getElementById('installBanner');
    if(ban) ban.classList.remove('show');
  }
  if(e.target && e.target.id === 'dismissInstallBtn'){
    const ban = document.getElementById('installBanner');
    if(ban) ban.classList.remove('show');
  }
});
'''


def main() -> None:
    html = SRC.read_text()

    html = html.replace(
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Cadence</title>',
        '''<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>Cadence</title>
<meta name="description" content="Cadence — social fitness, programming, and free nutrition tools.">
<meta name="theme-color" content="#d94f1e">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Cadence">
<link rel="manifest" href="./manifest.json">
<link rel="apple-touch-icon" href="./icon-192.png">
<link rel="icon" type="image/png" sizes="192x192" href="./icon-192.png">
<link rel="icon" type="image/png" sizes="512x512" href="./icon-512.png">'''
    )
    html = html.replace(
        'https://unpkg.com/lucide@latest/dist/umd/lucide.js',
        'https://unpkg.com/lucide@0.544.0/dist/umd/lucide.js'
    )
    html = html.replace(
        'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2',
        'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.57.4'
    )
    html = html.replace('</style>', FREE_CSS + '\n</style>')
    html = html.replace(
        '<button class="nav-item" data-view="programs"><svg data-lucide="dumbbell"></svg><span>Programs</span></button>',
        '<button class="nav-item" data-view="programs"><svg data-lucide="dumbbell"></svg><span>Programs</span></button>\n    <button class="nav-item" data-view="free"><svg data-lucide="calculator"></svg><span>Free Tools</span></button>'
    )
    html = html.replace(
        '''      <button aria-label="Activity"><svg data-lucide="heart"></svg></button>
      <button aria-label="Messages"><svg data-lucide="send"></svg></button>''',
        '''      <button aria-label="Install app" id="iosInstallHint"><svg data-lucide="download"></svg></button>
      <button aria-label="Activity"><svg data-lucide="heart"></svg></button>
      <button aria-label="Messages" data-view="messages"><svg data-lucide="send"></svg></button>'''
    )
    html = html.replace(
        '<div id="feedPosts"></div>\n    </section>',
        '''<div id="installBanner" class="install-banner">
        <p><strong>Install Cadence</strong>Add to your home screen for the full-screen phone app.</p>
        <button class="btn btn-primary" id="installAppBtn" type="button">Install</button>
        <button class="btn btn-ghost" id="dismissInstallBtn" type="button">Not now</button>
      </div>
      <div id="feedPosts"></div>
    </section>'''
    )
    html = html.replace(
        '    <!-- EXPLORE VIEW -->',
        FREE_VIEW + '\n    <!-- EXPLORE VIEW -->'
    )
    html = html.replace(
        '<button class="more-drawer-item" data-view="programs"><svg data-lucide="dumbbell"></svg>Programs</button>',
        '<button class="more-drawer-item" data-view="programs"><svg data-lucide="dumbbell"></svg>Programs</button>\n    <button class="more-drawer-item" data-view="free"><svg data-lucide="calculator"></svg>Free Tools</button>'
    )
    html = html.replace('await supabase', 'await sb')
    html = html.replace(
        "const sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);",
        "const sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);\nconst supabase = sb;"
    )
    html = html.replace(
        "(function(){const t=document.querySelector('[data-theme-toggle]'),r=document.documentElement;let d=matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light';r.setAttribute('data-theme',d);t&&t.addEventListener('click',()=>{d=d==='dark'?'light':'dark';r.setAttribute('data-theme',d)})})();",
        """(function(){const t=document.querySelector('[data-theme-toggle]'),r=document.documentElement;const saved=localStorage.getItem('cd-theme');let d=saved|| (matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');r.setAttribute('data-theme',d);t&&t.addEventListener('click',()=>{d=d==='dark'?'light':'dark';r.setAttribute('data-theme',d);localStorage.setItem('cd-theme',d)})})();"""
    )
    html = html.replace(
        "  if(name === 'reels') renderReels();\n  if(name === 'whiteboard') renderWhiteboard();\n  if(name === 'profile' && !opts.fromHash) loadProfileByUsername(opts.username || null);",
        "  if(name === 'reels') renderReels();\n  if(name === 'whiteboard') renderWhiteboard();\n  if(name === 'free') initMacroCalculator();\n  if(name === 'profile' && !opts.fromHash) loadProfileByUsername(opts.username || null);"
    )
    html = html.replace(
        "    } else if(name === 'reels'){\n      if(window.location.hash !== '#reels') history.pushState(null, '', '#reels');",
        "    } else if(name === 'reels'){\n      if(window.location.hash !== '#reels') history.pushState(null, '', '#reels');\n    } else if(name === 'free'){\n      if(window.location.hash !== '#free') history.pushState(null, '', '#free');"
    )
    html = html.replace(
        "  } else if(route === 'reels'){\n    setView('reels', { skipHash: true });\n  }",
        "  } else if(route === 'reels'){\n    setView('reels', { skipHash: true });\n  } else if(route === 'free'){\n    setView('free', { skipHash: true });\n  }"
    )
    html = html.replace(
        "    feedPosts.unshift({...original, user:users[0], repostOf:original.user, likes:0, time:'JUST NOW', tags:[]});\n    renderFeed();",
        "    feedPosts.unshift({...original, user:users[0], repostOf:original.user, likes:0, time:'JUST NOW', tags:[]});\n    if(typeof renderLiveFeed==='function') renderLiveFeed();"
    )
    html = html.replace(
        "initApp().then(()=>{ handleHashRoute(); });",
        "if(typeof renderFeed!=='function'){ window.renderFeed = function(){ if(typeof renderLiveFeed==='function') return renderLiveFeed(); }; }\n"
        + PWA_JS
        + FREE_JS
        + "\ninitApp().then(()=>{ handleHashRoute(); initMacroCalculator(); });\n"
        + "const iosHint=document.getElementById('iosInstallHint');\n"
        + "if(iosHint) iosHint.addEventListener('click',()=>showToast('On iPhone: Share → Add to Home Screen'));\n"
    )

    (ROOT / "index.html").write_text(html)
    print("wrote index.html", len(html))

    (ROOT / "manifest.json").write_text(
        """{
  "name": "Cadence",
  "short_name": "Cadence",
  "description": "Social fitness, programming, and free nutrition tools",
  "start_url": "./",
  "scope": "./",
  "display": "standalone",
  "orientation": "portrait",
  "background_color": "#121110",
  "theme_color": "#d94f1e",
  "icons": [
    {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
    {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
    {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
    {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
  ]
}
"""
    )
    (ROOT / "sw.js").write_text(
        """const CACHE = 'cadence-v3';
const PRECACHE = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png'];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((cache) => cache.put('./index.html', copy));
        return res;
      }).catch(() => caches.match('./index.html'))
    );
    return;
  }
  event.respondWith(
    caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      const copy = res.clone();
      caches.open(CACHE).then((cache) => cache.put(req, copy));
      return res;
    }))
  );
});
"""
    )
    (ROOT / "_headers").write_text(
        """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Content-Security-Policy: default-src 'self'; img-src 'self' data: blob: https:; media-src 'self' blob: https:; style-src 'self' 'unsafe-inline' https://api.fontshare.com https://fonts.googleapis.com; font-src https://api.fontshare.com https://fonts.gstatic.com data:; script-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net; connect-src 'self' https://stezlxsdtjxieckqvhba.supabase.co https://*.supabase.co wss://stezlxsdtjxieckqvhba.supabase.co;

/sw.js
  Cache-Control: no-cache
"""
    )
    (ROOT / "_redirects").write_text("/*    /index.html   200\n")
    write_png(ROOT / "icon-192.png", 192, cadence_icon)
    write_png(ROOT / "icon-512.png", 512, cadence_icon)
    print("icons + pwa files written")


if __name__ == "__main__":
    main()
