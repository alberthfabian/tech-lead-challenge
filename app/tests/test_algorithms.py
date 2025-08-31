from app.algorithms.top_customers import top_k_customers
from app.algorithms.transit_routes import TransitIndex

def test_top_customers():
    rows = [
        (1,"u1",100), (2,"u2",100), (3,"u1",50),
        (4,"u3",70), (5,"u2",20), (6,"u1",10),
    ]
    assert top_k_customers(rows, 1, 6, 2)[0][0] == "u1"

def test_transit_index():
    idx = TransitIndex()
    idx.add_route("R1", {"S1","S2"})
    idx.add_stop("R1", "S3")
    assert "R1" in idx.routes_by("S2")
    idx.remove_stop("R1","S2")
    assert "R1" not in idx.routes_by("S2")
