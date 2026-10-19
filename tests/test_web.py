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
    assert 'id="finalCard" class="card final-card" hidden' in response.text
    assert "#run{grid-column:1/-1;width:100%}" in response.text
    assert ".left-stack{display:flex;flex-direction:column;gap:0" in response.text


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
