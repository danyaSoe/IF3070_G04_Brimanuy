from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from service.runner import ALGORITHMS, run_simulation
from web.schemas import SimulationRequest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
app = FastAPI(title="Brimanuy Cargo Deck Simulator", version="1.0.0")


@app.get("/", response_class=HTMLResponse)
def index():
    return """<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Brimanuy Cargo Deck Simulator</title>
<style>
:root{color-scheme:dark}
:root{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#1f2937;background:#f3f4f6}
*{box-sizing:border-box}body{margin:0}.shell{width:100%;margin:0;padding:20px 32px}[hidden]{display:none!important}
header{display:flex;justify-content:center;align-items:center;margin-bottom:18px;text-align:center}
h1{margin:0;font-size:42px;letter-spacing:-.045em;font-weight:750;color:#2392B9}h1 span{color:#F4DB40}h2{font-size:15px;line-height:1.4;letter-spacing:.09em;text-transform:uppercase;font-weight:700;color:#6b7280;margin:0 0 12px}.muted{color:#6b7280;font-size:15px}
.panel,.card{background:#fff;border:1px solid #e5e7eb;border-radius:10px;box-shadow:0 1px 2px #11182708}
.controls{padding:16px;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;align-items:end}
label{display:flex;flex-direction:column;gap:7px;font-size:15px;font-weight:600;color:#4b5563}
select,input,button{font:inherit;border:1px solid #d1d5db;border-radius:7px;padding:10px 12px;background:#fff;color:#1f2937}
select:focus,input:focus{outline:2px solid #cbd5e1;outline-offset:1px;border-color:#9ca3af}
button{background:#374151;color:#fff;border:1px solid #374151;font-weight:650;cursor:pointer;transition:background .15s,border-color .15s}
button:hover:not(:disabled){background:#1f2937;border-color:#1f2937}button:disabled{opacity:.55;cursor:wait}
#run{grid-column:1/-1;width:100%}
#parameters{grid-column:1/-1;display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:12px;padding-top:4px;width:100%}
#parameters label{min-width:0}.dashboard-layout{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:18px;margin-top:18px;align-items:start}
.left-stack{display:flex;flex-direction:column;gap:0;min-width:0;align-self:start}.left-stack > .status{margin:6px 0 0}.final-card{min-width:0;min-height:620px;display:flex;flex-direction:column}.final-card .ships{flex:1;min-height:0}
#dashboard{display:block}.summary-card{display:block;width:100%;min-width:0;overflow:hidden}
.card{padding:16px}.summary-card h2{text-align:center}.summary-card>h2:first-child,.final-card>h2{font-size:18px;letter-spacing:-.02em;text-transform:none;color:#111827;margin-bottom:14px}
.result-list{display:grid;gap:0}.result-row{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid #f1f2f4}
.result-row:last-child{border-bottom:0}.result-row>span:first-child{color:#6b7280;font-size:15px;font-weight:500}.result-row strong{font-size:16px;font-weight:650;color:#111827;text-align:right}
.result-list.tile-grid{display:flex;flex-direction:column;gap:10px}
.tile-grid .result-group{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.tile-grid .result-group.bottom{display:flex;justify-content:center;gap:10px}
.tile-grid .result-group .result-row{flex:0 1 calc((100% - 30px)/4)}
.tile-grid .result-row{min-width:0;min-height:88px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;padding:12px;border:0;border-radius:0;background:transparent;text-align:center}
.tile-grid .result-row>span:first-child{font-size:17px;line-height:1.35;text-align:center}.tile-grid .result-row strong{font-size:24px;text-align:center;overflow-wrap:anywhere}
.badge{display:inline-flex;align-items:center;min-height:26px;padding:4px 10px;border-radius:999px;background:#f3f4f6;color:#4b5563;font-size:14px;font-weight:650;white-space:nowrap}
.badge.good{background:#ecfdf3;color:#067647}.badge.bad{background:#fef3f2;color:#b42318}
.empty-placeholder{display:flex;align-items:center;justify-content:center;color:#667085}
.deck-placeholder{height:240px;border:2px solid #d0d5dd;border-radius:4px;background:#f8fafc}
.ships{display:flex;flex-direction:column;align-content:stretch;gap:14px;max-height:100%;overflow-y:auto;padding:2px 4px 2px 2px}.ship-wrap{flex:0 0 auto;width:100%;min-width:0}.ship-title{display:flex;justify-content:space-between;margin-bottom:7px;font-weight:650;font-size:15px;color:#374151}
.deck{position:relative;width:100%;background-color:#f8fafc;border:1px solid #9ca3af;border-radius:4px;
background-image:linear-gradient(#e5e7eb 1px,transparent 1px),linear-gradient(90deg,#e5e7eb 1px,transparent 1px);
background-size:var(--cell-width) var(--cell-height);overflow:hidden}
.vehicle{position:absolute;border:1px solid #fff;border-radius:3px;color:#283548;font-size:13px;font-weight:700;
display:flex;align-items:center;justify-content:center;overflow:hidden;box-shadow:0 1px 2px #1118271a}
.outside{display:flex;flex-wrap:wrap;justify-content:center;gap:12px;padding-bottom:20px}
.outside-item{display:flex;flex-direction:column;align-items:center;justify-content:center;aspect-ratio:1;min-width:150px;padding:18px;font-size:16px;line-height:1.5;text-align:center;background:#f9fafb;color:#374151}
.summary-card h2:not(:first-child){margin-top:22px}.chart-area{position:relative;width:100%;height:auto;aspect-ratio:1000/480;flex:none;overflow:hidden}.chart{display:block;width:100%;height:100%;min-height:0;overflow:hidden}.chart .grid-line{stroke:#26364b;stroke-width:1}.chart .axis-line{stroke:#718096;stroke-width:1}.chart text{fill:#aab7c8;font-family:system-ui,sans-serif;font-size:13px;font-weight:400;letter-spacing:normal}.chart .axis-label{fill:#e2e8f0;font-size:14px;font-weight:600}.chart polyline{fill:none;stroke:#2392B9;stroke-width:2.5}
.status{min-height:20px;margin-top:10px;font-size:15px;color:#6b7280}.error{color:#b42318}
@media(max-width:850px){.controls{grid-template-columns:repeat(2,minmax(0,1fr))}.tile-grid .result-group{grid-template-columns:repeat(2,minmax(0,1fr))}.tile-grid .result-group.bottom{display:grid;grid-template-columns:repeat(6,minmax(0,1fr))}.tile-grid .result-group.bottom .result-row{grid-column:span 2}header{display:block}.ships{max-height:470px}}
@media(max-width:480px){.tile-grid .result-group,.tile-grid .result-group.bottom{grid-template-columns:1fr}.tile-grid .result-group.bottom .result-row{grid-column:span 1}.tile-grid .result-group.bottom{display:grid}}
/* Dark surfaces keep the two brand accents crisp and readable. */
body{background:#0b1220;color:#e5e7eb}
.panel,.card{background:#111c2e;border-color:#263449;box-shadow:0 1px 2px #0004}
h1{color:#2392B9}h1 span{color:#F4DB40}
h2,.summary-card>h2:first-child,.final-card>h2{color:#e5edf7}
.muted,.result-row>span:first-child,.chart text{color:#aab7c8;fill:#aab7c8}
label{color:#cbd5e1}
select,input{background:#0b1220;color:#e5e7eb;border-color:#3a4a60}
select:focus,input:focus{outline-color:#2392B9;border-color:#2392B9}
button{background:#2392B9;border-color:#2392B9;color:#07111d}
button:hover:not(:disabled){background:#34a7d0;border-color:#34a7d0}
.result-row{border-color:#263449}.result-row strong{color:#f8fafc}
.badge{background:#263449;color:#dbe5f2}.badge.good{background:#12372f;color:#86efac}.badge.bad{background:#48262a;color:#fda4af}
.deck{background-color:#18263a;border-color:#52647b;background-image:linear-gradient(#33445c 1px,transparent 1px),linear-gradient(90deg,#33445c 1px,transparent 1px)}
.vehicle{border-color:#111c2e;color:#111827;box-shadow:0 1px 3px #0006}
.outside-item{background:#162337;border-color:#33445c;color:#e2e8f0}
.deck-placeholder{background:#162337;border-color:#33445c}
.chart .grid-line{stroke:#26364b}.chart .axis-line{stroke:#718096}.chart .axis-label{fill:#e2e8f0}
.status{color:#aab7c8}.error{color:#fda4af}
</style></head>
<body><main class="shell"><header><div><h1>Brimanuy <span>Cargo Deck</span></h1>
<div class="muted">Local Search Simulator</div></div></header>
<div id="appLayout" class="dashboard-layout"><div class="left-stack"><section class="panel controls">
<label>Case JSON<select id="caseSelect"><option value="src/data/case1.json">case1.json</option>
<option value="src/data/case_multi.json">case_multi.json</option></select></label>
<label>Algoritma<select id="algorithm" onchange="renderParameters()">
<option value="ga">Genetic Algorithm</option><option value="sa">Simulated Annealing</option>
<option value="steepest">Steepest Ascent</option><option value="sideways">Sideways Move</option>
<option value="stochastic">Stochastic Hill-Climbing</option><option value="random_restart">Random Restart</option></select></label>
<label>Objective<select id="mode"><option value="fee">Shipping Fee</option>
<option value="urgency">Urgency</option><option value="area">Area</option></select></label>
<label>Seed<input id="seed" type="number" value="0"></label>
<div id="parameters"></div><button id="run" onclick="runSimulation()">Run Simulation</button>
</section><div id="status" class="status"></div>
<section id="dashboard"><div class="card summary-card"><h2>HASIL SIMULASI</h2><div id="results" class="result-list tile-grid"><div class="result-group top">
<div class="result-row"><span>Feasible</span><strong id="feasible"><span class="badge">-</span></strong></div>
<div class="result-row"><span>Score</span><strong id="score">-</strong></div>
<div class="result-row"><span>Penalty</span><strong id="penalty">-</strong></div>
<div class="result-row"><span>Kapasitas</span><strong id="capacity"><span class="badge">-</span></strong></div>
</div><div class="result-group bottom">
<div class="result-row"><span>Kendaraan dimuat</span><strong id="loaded">-</strong></div>
<div class="result-row"><span>Iterasi/generasi</span><strong id="iterations">-</strong></div>
<div class="result-row"><span>Durasi</span><strong id="duration">-</strong></div></div></div>
<h2 style="margin-top:22px">Kendaraan di luar kapal</h2><div id="outside" class="outside empty-placeholder">-</div>
<h2 style="margin-top:22px">Perkembangan objective</h2><div id="chartArea" class="chart-area"><svg id="chart" class="chart" viewBox="0 0 1000 480" preserveAspectRatio="xMinYMid meet">
<g id="chartGrid"></g><g id="chartTicks"></g><line class="axis-line" x1="80" y1="390" x2="980" y2="390"></line>
<line class="axis-line" x1="80" y1="40" x2="80" y2="390"></line><polyline id="line" points=""></polyline>
<text class="axis-label" x="530" y="455" text-anchor="middle">Iterasi / generasi</text>
<text class="axis-label" transform="translate(20 215) rotate(-90)" text-anchor="middle">Objective</text></svg></div></div></section></div>
<aside id="finalCard" class="card final-card"><h2>Final state: susunan geladak</h2>
<div id="ships" class="ships"><div class="empty-placeholder deck-placeholder">-</div></div></aside></div>
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
function fmt(v,digits=2){return new Intl.NumberFormat('en-US',{useGrouping:false,maximumFractionDigits:digits}).format(Number(v)).replace('.',',');}
function color(){return '#F4DB40';}
function badge(text,tone=''){return `<span class="badge ${tone}">${text}</span>`;}
function renderState(data){const shipsEl=document.getElementById('ships');shipsEl.innerHTML='';
outside.classList.remove('empty-placeholder');
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
renderChart(data.history);}
function renderEmptyChart(){const left=80,right=980,top=40,bottom=390,count=4;
chartGrid.innerHTML=Array.from({length:count+1},(_,i)=>{const y=top+(i/count)*(bottom-top);
return `<line class="grid-line" x1="${left}" y1="${y}" x2="${right}" y2="${y}"></line>`;}).join('')+
Array.from({length:count+1},(_,i)=>{const x=left+(i/count)*(right-left);
return `<line class="grid-line" x1="${x}" y1="${top}" x2="${x}" y2="${bottom}"></line>`;}).join('');
chartTicks.innerHTML=Array.from({length:count+1},(_,i)=>{const y=top+(i/count)*(bottom-top);
return `<text x="${left-8}" y="${y+4}" text-anchor="end">-</text>`;}).join('')+
Array.from({length:count+1},(_,i)=>{const x=left+(i/count)*(right-left);
return `<text x="${x}" y="${bottom+18}" text-anchor="middle">-</text>`;}).join('');
line.setAttribute('points','');}
function renderChart(points){const left=80,right=980,top=40,bottom=390,count=4;
const min=Math.min(...points),max=Math.max(...points),range=max-min||1;
const yMin=min-(range===1?0.5:range*0.05),yMax=max+(range===1?0.5:range*0.05),yRange=yMax-yMin;
const xAt=i=>left+(i/(points.length-1||1))*(right-left),yAt=v=>bottom-((v-yMin)/yRange)*(bottom-top);
chartGrid.innerHTML=Array.from({length:count+1},(_,i)=>{const value=yMin+(yRange/count)*i,y=yAt(value);
return `<line class="grid-line" x1="${left}" y1="${y}" x2="${right}" y2="${y}"></line>`;}).join('');
chartTicks.innerHTML=Array.from({length:count+1},(_,i)=>{const value=yMin+(yRange/count)*i,y=yAt(value);
return `<text x="${left-8}" y="${y+4}" text-anchor="end">${Math.round(value)}</text>`;}).join('')+
Array.from(new Set(Array.from({length:count+1},(_,i)=>Math.round((points.length-1)*i/count)))).map(index=>{const x=xAt(index);
return `<line class="grid-line" x1="${x}" y1="${top}" x2="${x}" y2="${bottom}"></line><text x="${x}" y="${bottom+18}" text-anchor="middle">${index}</text>`;}).join('');
line.setAttribute('points',points.map((v,i)=>`${xAt(i)},${yAt(v)}`).join(' '));}
async function runSimulation(){const button=document.getElementById('run');button.disabled=true;status.className='status';status.textContent='Menjalankan simulasi...';
try{const response=await fetch('/api/simulate',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({case:caseSelect.value,algorithm:algorithm.value,mode:mode.value,seed:Number(seed.value),parameters:params()})});
const data=await response.json();if(!response.ok)throw new Error(data.detail||'Simulasi gagal');
iterations.textContent=fmt(data.iterations);
duration.textContent=fmt(data.duration,3)+' s';loaded.textContent=data.final_state.filter(p=>p[0]>=0).length+'/'+data.vehicles.length;
feasible.innerHTML=badge(data.feasible?'Yes':'No',data.feasible?'good':'bad');score.textContent=fmt(data.score_before_penalty);penalty.textContent=fmt(data.penalty);
capacity.innerHTML=badge(data.capacity_ok?'OK':'Melebihi kapasitas',data.capacity_ok?'good':'bad');
renderState(data);status.textContent='Simulasi selesai.';}
catch(error){status.className='status error';status.textContent=error.message;}finally{button.disabled=false;}}
renderParameters();renderEmptyChart();
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
