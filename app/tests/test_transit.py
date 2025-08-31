# app/tests/test_transit.py
from app.algorithms.transit_routes import TransitIndex

def test_transit_index_basic():
    """
    Test basic functionality of TransitIndex.
    """
    idx = TransitIndex()
    idx.add_route("R1", {"A","B"})
    idx.add_stop_to_route("R1","C")
    assert "R1" in idx.get_routes_by_stop("A")
    assert idx.get_stops_by_route("R1") == {"A","B","C"}

    idx.remove_stop_from_route("R1","B")
    assert "R1" not in idx.get_routes_by_stop("B")
    assert idx.get_stops_by_route("R1") == {"A","C"}

    idx.add_route("R2", {"C"})
    assert "R2" in idx.get_routes_by_stop("C")
    idx.remove_route("R1")
    assert "R1" not in idx.get_routes_by_stop("A")
