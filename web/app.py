from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from service.runner import ALGORITHMS, run_simulation
from web.schemas import SimulationRequest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title="Brimanuy Cargo Deck Simulator", version="1.0.0")


@app.get("/", response_class=HTMLResponse)
def index():
    return """<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Brimanuy Cargo Deck Simulator</title>
<style>
:root{font-family:Inter,system-ui,sans-serif;color:#182230;background:#f5f7fb}
*{box-sizing:border-box}body{margin:0}.shell{max-width:1280px;margin:auto;padding:28px}
header{display:flex;justify-content:space-between;align-items:end;margin-bottom:22px}
h1{margin:0;font-size:28px}h2{font-size:18px;margin:0 0 14px}.muted{color:#667085;font-size:13px}
.panel,.card{background:#fff;border:1px solid #e4e7ec;border-radius:14px;box-shadow:0 2px 8px #1018280d}
.controls{padding:18px;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;align-items:end}
label{display:flex;flex-direction:column;gap:6px;font-size:13px;font-weight:600;color:#344054}
select,input,button{font:inherit;border:1px solid #d0d5dd;border-radius:8px;padding:9px;background:#fff}
button{background:#155eef;color:#fff;border:0;font-weight:700;cursor:pointer}button:disabled{opacity:.55;cursor:wait}
#run{grid-column:1/-1;width:100%}
#parameters{grid-column:1/-1;display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:12px;padding-top:4px;width:100%}
#parameters label{min-width:0}.dashboard-layout{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(360px,.85fr);gap:18px;margin-top:18px;align-items:stretch}
.left-stack{display:flex;flex-direction:column;gap:0;min-width:0}.left-stack > .status{margin:6px 0 0}.dashboard-layout.no-final{grid-template-columns:1fr}.final-card{min-width:0;display:flex;flex-direction:column}.final-card[hidden]{display:none}.final-card .ships{flex:1;min-height:0}
.card{padding:18px}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:18px}
.metric{background:#f8fafc;border-radius:10px;padding:12px}.metric strong{display:block;font-size:21px;margin-top:4px}
.ships{display:flex;flex-direction:column;align-content:stretch;gap:18px;max-height:100%;overflow-y:auto;padding:2px 4px 2px 2px}.ship-wrap{flex:0 0 auto;width:100%;min-width:0}.ship-title{display:flex;justify-content:space-between;margin-bottom:8px;font-weight:700;font-size:13px}
.deck{position:relative;width:100%;background-color:#eef2f6;border:2px solid #344054;
background-image:linear-gradient(#cbd5e1 1px,transparent 1px),linear-gradient(90deg,#cbd5e1 1px,transparent 1px);
background-size:var(--cell-width) var(--cell-height);overflow:hidden}
.vehicle{position:absolute;border:2px solid #fff;border-radius:5px;color:#fff;font-size:11px;font-weight:800;
display:flex;align-items:center;justify-content:center;overflow:hidden;box-shadow:0 2px 4px #10182833}
.outside{display:flex;flex-wrap:wrap;gap:8px}
.outside-item{border:1px solid #d0d5dd;border-radius:8px;padding:8px;font-size:12px;background:#f8fafc}
.summary-card h2:not(:first-child){margin-top:22px}.chart{width:100%;height:190px}.chart polyline{fill:none;stroke:#155eef;stroke-width:2}
.status{min-height:20px;margin-top:10px;font-size:13px}.error{color:#b42318}
@media(max-width:850px){.controls{grid-template-columns:repeat(2,minmax(0,1fr))}.dashboard-layout{grid-template-columns:1fr}.metrics{grid-template-columns:repeat(2,1fr)}header{display:block}.ships{max-height:470px}}
</style></head>
<body><main class="shell"><header><div><h1>Brimanuy Cargo Deck</h1>
<div class="muted">Local Search Simulator</div></header>
<div id="appLayout" class="dashboard-layout no-final"><div class="left-stack"><section class="panel controls">
<label>Case JSON<select id="caseSelect"><option value="data/case1.json">case1.json</option>
<option value="data/case_multi.json">case_multi.json</option></select></label>
<label>Algoritma<select id="algorithm" onchange="renderParameters()">
<option value="ga">Genetic Algorithm</option><option value="sa">Simulated Annealing</option>
<option value="steepest">Steepest Ascent</option><option value="sideways">Sideways Move</option>
<option value="stochastic">Stochastic Hill-Climbing</option><option value="random_restart">Random Restart</option></select></label>
<label>Objective<select id="mode"><option value="fee">Shipping Fee</option>
<option value="urgency">Urgency</option><option value="area">Area</option></select></label>
<label>Seed<input id="seed" type="number" value="0"></label>
<div id="parameters"></div><button id="run" onclick="runSimulation()">Run Simulation</button>
</section><div id="status" class="status"></div>
<section id="dashboard" hidden><div class="metrics">
<div class="metric"><span class="muted">Final objective</span><strong id="value">-</strong></div>
<div class="metric"><span class="muted">Kendaraan dimuat</span><strong id="loaded">-</strong></div>
<div class="metric"><span class="muted">Iterasi/generasi</span><strong id="iterations">-</strong></div>
<div class="metric"><span class="muted">Durasi</span><strong id="duration">-</strong></div></div>
<div class="card summary-card"><h2>Ringkasan constraint</h2><div id="constraints"></div>
<h2 style="margin-top:22px">Kendaraan di luar kapal</h2><div id="outside" class="outside"></div>
<h2 style="margin-top:22px">Parameter digunakan</h2><div id="usedParams" class="muted"></div>
<h2 style="margin-top:22px">Perkembangan objective</h2><svg id="chart" class="chart" viewBox="0 0 600 190" preserveAspectRatio="none">
<polyline id="line" points=""></polyline></div></section></div>
<aside id="finalCard" class="card final-card" hidden><h2>Final state: susunan geladak</h2>
<div id="ships" class="ships"></div></aside></div>
</main><script>
const configs={
ga:[['pop_size','Population',50],['generations','Generations',200],['crossover_rate','Crossover rate',0.9],['mutation_rate','Mutation rate',0.2],['elitism','Elitism',2]],
sa:[['T0','Initial temperature',60],['alpha','Cooling rate',0.999],['T_min','Minimum temperature',0.01],['max_iter','Max iterations',100000]],
sideways:[['max_sideways','Max sideways moves',100]],
stochastic:[['max_iter','Max iterations',20000],['patience','No-improvement patience',2000]],
random_restart:[['max_restart','Max restarts',10]],steepest:[]};
function renderParameters(){parameters.innerHTML=(configs[algorithm.value]||[]).map(([id,label,value])=>
`<label>${label}<input id="param-${id}" type="number" step="${String(value).includes('.')?'0.001':'1'}" value="${value}"></label>`).join('');}
function params(){return Object.fromEntries((configs[algorithm.value]||[]).map(([id])=>[id,Number(document.getElementById('param-'+id).value)]));}
function fmt(v){return Number(v).toLocaleString('id-ID',{maximumFractionDigits:2});}
function color(i){return `hsl(${(i*47)%360} 68% 43%)`;}
function renderState(data){const shipsEl=document.getElementById('ships');shipsEl.innerHTML='';
const occupied=new Set(), byId=Object.fromEntries(data.vehicles.map((v,i)=>[v.id,{...v,i}]));
data.ships.forEach((ship,s)=>{const wrap=document.createElement('div');wrap.className='ship-wrap';
const load=data.ship_loads[s], title=document.createElement('div');title.className='ship-title';
title.innerHTML=`<span>${ship.id}</span><span class="muted">${load}/${ship.max_capacity} unit berat</span>`;
const deck=document.createElement('div');deck.className='deck';deck.style.aspectRatio=`${ship.w}/${ship.l}`;
deck.style.setProperty('--cell-width',`calc(100% / ${ship.w})`);
deck.style.setProperty('--cell-height',`calc(100% / ${ship.l})`);
data.final_state.forEach((p,i)=>{if(p[0]!==s)return;const v=data.vehicles[i], [w,l]=p[3]===0?[v.w,v.l]:[v.l,v.w];
const el=document.createElement('div');el.className='vehicle';el.style.left=p[1]*26+'px';el.style.top=p[2]*26+'px';
el.style.left=`${p[1]/ship.w*100}%`;el.style.top=`${p[2]/ship.l*100}%`;
el.style.width=`${w/ship.w*100}%`;el.style.height=`${l/ship.l*100}%`;
el.style.background=color(i);el.textContent=v.id;
el.title=`${v.id} | ${w}x${l} | fee ${v.fee} | berat ${v.weight} | ${p[3]===0?'Horizontal':'Vertical'}`;deck.appendChild(el);});
wrap.append(title,deck);shipsEl.appendChild(wrap);});
outside.innerHTML=data.final_state.map((p,i)=>p[0]<0?`<div class="outside-item"><b>${data.vehicles[i].id}</b><br>${data.vehicles[i].w}x${data.vehicles[i].l} · fee ${data.vehicles[i].fee}</div>`:'').join('')||'<span class="muted">Semua kendaraan dimuat.</span>';
const points=data.history, min=Math.min(...points), max=Math.max(...points), span=max-min||1;
line.setAttribute('points',points.map((v,i)=>`${(i/(points.length-1||1))*600},${175-((v-min)/span)*160}`).join(' '));}
async function runSimulation(){const button=document.getElementById('run');button.disabled=true;status.className='status';status.textContent='Menjalankan simulasi...';
try{const response=await fetch('/api/simulate',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({case:caseSelect.value,algorithm:algorithm.value,mode:mode.value,seed:Number(seed.value),parameters:params()})});
const data=await response.json();if(!response.ok)throw new Error(data.detail||'Simulasi gagal');
dashboard.hidden=false;finalCard.hidden=false;appLayout.classList.remove('no-final');value.textContent=fmt(data.final_value);iterations.textContent=fmt(data.iterations);
duration.textContent=data.duration.toFixed(3)+' s';loaded.textContent=data.final_state.filter(p=>p[0]>=0).length+'/'+data.vehicles.length;
constraints.innerHTML=`<p><b>${data.feasible?'✓ Feasible':'✕ Tidak feasible'}</b></p><p>Score: ${fmt(data.score_before_penalty)}</p><p>Penalty: ${fmt(data.penalty)}</p><p>Kapasitas: ${data.capacity_ok?'OK':'Melebihi kapasitas'}</p>`;
usedParams.innerHTML=Object.entries(params()).map(([k,v])=>`<div><b>${k}</b>: ${v}</div>`).join('');renderState(data);status.textContent='Simulasi selesai.';}
catch(error){status.className='status error';status.textContent=error.message;}finally{button.disabled=false;}}
renderParameters();
</script></body></html>"""


@app.get("/api/algorithms")
def algorithms():
    return {"algorithms": sorted(ALGORITHMS)}


@app.post("/api/simulate")
def simulate(request: SimulationRequest):
    case_path = (PROJECT_ROOT / request.case).resolve()
    try:
        case_path.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Case harus berada di project.") from exc
    if not case_path.is_file():
        raise HTTPException(status_code=404, detail="File case tidak ditemukan.")
    try:
        return run_simulation(
            case_path, request.algorithm, request.mode,
            request.seed, request.parameters,
        )
    except (ValueError, KeyError, OSError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
