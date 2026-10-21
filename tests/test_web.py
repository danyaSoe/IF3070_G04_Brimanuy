from fastapi.testclient import TestClient

from web.app import app


client = TestClient(app)


def test_algorithms_endpoint():
    response = client.get("/api/algorithms")
    assert response.status_code == 200
    assert "ga" in response.json()["algorithms"]


def test_home_page_contains_visual_dashboard():
    response = client.get("/")
    assert response.status_code == 200
    assert "Final state: susunan geladak" in response.text
    assert "renderState" in response.text
    assert 'class="dashboard-layout"' in response.text
    assert 'id="dashboard"><div class="card summary-card"><h2>HASIL SIMULASI</h2>' in response.text
    assert '<span>Feasible</span><strong id="feasible"><span class="badge">-</span></strong>' in response.text
    assert '<span>Score</span><strong id="score">-</strong>' in response.text
    assert '<span>Penalty</span><strong id="penalty">-</strong>' in response.text
    assert 'id="results" class="result-list tile-grid"' in response.text
    assert "Parameter digunakan" not in response.text
    assert '<span>Kendaraan dimuat</span><strong id="loaded">-</strong>' in response.text
    assert '<span>Iterasi/generasi</span><strong id="iterations">-</strong>' in response.text
    assert '<span>Durasi</span><strong id="duration">-</strong>' in response.text
    assert "Ringkasan constraint</h2>" not in response.text
    assert ".result-list.tile-grid{display:flex;flex-direction:column;gap:10px}" in response.text
    assert ".tile-grid .result-group{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}" in response.text
    assert ".tile-grid .result-group.bottom{display:flex;justify-content:center;gap:10px}" in response.text
    assert ".tile-grid .result-group .result-row{flex:0 1 calc((100% - 30px)/4)}" in response.text
    assert ".tile-grid .result-row{min-width:0;min-height:88px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;padding:12px;border:0;border-radius:0;background:transparent;text-align:center}" in response.text
    assert ".tile-grid .result-row>span:first-child{font-size:17px;line-height:1.35;text-align:center}.tile-grid .result-row strong{font-size:24px;text-align:center;overflow-wrap:anywhere}" in response.text
    assert "@media(max-width:850px){.controls{grid-template-columns:repeat(2,minmax(0,1fr))}.tile-grid .result-group{grid-template-columns:repeat(2,minmax(0,1fr))}" in response.text
    assert ".outside{display:flex;flex-wrap:wrap;justify-content:center;gap:12px;padding-bottom:20px}" in response.text
    assert "aspect-ratio:1;min-width:150px;padding:18px" in response.text
    assert "function renderUsedParams" not in response.text
    assert 'id="chartGrid"' in response.text
    assert 'id="chartTicks"' in response.text
    assert 'Iterasi / generasi' in response.text
    assert '>Objective</text>' in response.text
    assert 'viewBox="0 0 1000 480"' in response.text
    assert "[hidden]{display:none!important}" in response.text
    assert "height:auto;aspect-ratio:1000/480;flex:none" in response.text
    assert '<div id="chartArea" class="chart-area">' in response.text
    assert 'id="chart" class="chart" viewBox="0 0 1000 480" preserveAspectRatio="xMinYMid meet">' in response.text
    assert ".summary-card{display:block;width:100%;min-width:0;overflow:hidden}" in response.text
    assert ".chart-area{position:relative;width:100%;height:auto;aspect-ratio:1000/480;flex:none" in response.text
    assert ".dashboard-layout{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:18px;margin-top:18px;align-items:start}" in response.text
    assert ".summary-card h2{text-align:center}" in response.text
    assert ".outside{display:flex;flex-wrap:wrap;justify-content:center;gap:12px;padding-bottom:20px}" in response.text
    assert ".outside-item{display:flex;flex-direction:column;align-items:center;justify-content:center;aspect-ratio:1;min-width:150px" in response.text
    assert 'preserveAspectRatio="xMinYMid meet"' in response.text
    assert "font-family:system-ui,sans-serif;font-size:13px;font-weight:400;letter-spacing:normal" in response.text
    assert "useGrouping:false" in response.text
    assert "${Math.round(value)}" in response.text
    assert "new Set(Array.from({length:count+1}" in response.text
    assert "function renderEmptyChart()" in response.text
    assert "renderParameters();renderEmptyChart();" in response.text
    assert '<text x="${x}" y="${bottom+18}" text-anchor="middle">-</text>' in response.text
    assert 'id="ships" class="ships"><div class="empty-placeholder deck-placeholder">-' in response.text
    assert 'id="finalCard" class="card final-card"' in response.text
    assert "background:#374151;color:#fff" in response.text
    assert ".card{padding:16px}" in response.text
    assert ".result-row>span:first-child{color:#6b7280;font-size:15px;font-weight:500}" in response.text
    assert ".badge.good{background:#ecfdf3;color:#067647}" in response.text
    assert "function color(){return '#F4DB40';}" in response.text
    assert "function badge(text,tone='')" in response.text
    assert "color-scheme:dark" in response.text
    assert "Brimanuy <span>Cargo Deck</span>" in response.text
    assert "color:#2392B9" in response.text
    assert "color:#F4DB40" in response.text
    assert "font-size:42px" in response.text
    assert ".summary-card>h2:first-child,.final-card>h2{font-size:18px" in response.text
    assert ".chart text{fill:#aab7c8;font-family:system-ui,sans-serif;font-size:13px" in response.text
    assert "#run{grid-column:1/-1;width:100%}" in response.text
    assert ".left-stack{display:flex;flex-direction:column;gap:0" in response.text
    assert ".shell{width:100%;margin:0;padding:20px 32px}" in response.text
    assert ".dashboard-layout.no-final" not in response.text


def test_simulation_endpoint():
    response = client.post("/api/simulate", json={
        "case": "data/case1.json",
        "algorithm": "ga",
        "seed": 0,
        "parameters": {"pop_size": 4, "generations": 1, "elitism": 1},
    })
    assert response.status_code == 200
    assert response.json()["feasible"] is True
    assert len(response.json()["ships"]) == 1
    assert "final_mapping" in response.json()


def test_simulation_rejects_path_escape():
    response = client.post("/api/simulate", json={"case": "../secret.json"})
    assert response.status_code == 400
