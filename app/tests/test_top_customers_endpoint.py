import csv, gzip, os
from fastapi.testclient import TestClient
from app.main import app

def _make_small_csv(path):
    with gzip.open(path, "wt", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["timestamp","customer_id","amount"])
        rows = [
            (1,"A",100),(2,"B",100),(3,"A",50),
            (4,"C",70),(5,"B",20),(6,"A",10),
        ]
        for r in rows: w.writerow(r)

def test_top_customers_api_tmp(tmp_path):
    p = tmp_path/"transactions.csv.gz"
    _make_small_csv(p)
    client = TestClient(app)
    payload = {
        "path": str(p),
        "days": None,
        # usamos ventana explícita que incluye timestamps 1..6
        "start": "1970-01-01T00:00:00Z",
        "end": "1970-01-01T00:00:10Z",
        "top_customers": 2,
        "mode": "auto",
    }
    res = client.post("/api/v1/analytics/top-customers", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["results"][0]["customer_id"] == "A"
