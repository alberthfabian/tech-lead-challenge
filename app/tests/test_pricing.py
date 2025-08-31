def test_quote_basic(client):
    payload = {
        "stratum": 3,
        "items": [{"sku":"A", "price": 10000, "quantity": 3}]
    }
    res = client.post("/api/v1/orders/quote", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["subtotal"] == 30000
    assert data["total"] >= data["subtotal"]  # incluye envío
