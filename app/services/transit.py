"""
Services for managing transit routes and stops.
"""
from threading import RLock
from typing import Iterable, List
from app.algorithms.transit_routes import TransitIndex

_index = TransitIndex()
_lock = RLock()

def create_route(route_id: str, stops: Iterable[str]) -> None:
    """Returns True if the route was created, False if it already existed."""
    with _lock:
        if _index.get_stops_by_route(route_id):
            return False
        _index.add_route(route_id, stops)
        return True

def add_stop(route_id: str, stop_id: str) -> None:
    """Returns True if the relationship was created, False if it already existed."""
    with _lock:
        current = _index.get_stops_by_route(route_id)
        if stop_id in current:
            return False
        _index.add_stop_to_route(route_id, stop_id)
        return True

def remove_stop(route_id: str, stop_id: str) -> None:
    """Returns True if the relationship was removed, False if it did not exist."""
    with _lock:
        _index.remove_stop_from_route(route_id, stop_id)

def delete_route(route_id: str) -> None:
    """Returns True if the route was deleted, False if it did not exist."""
    with _lock:
        _index.remove_route(route_id)

def routes_by_stop(stop_id: str) -> List[str]:
    """Returns the routes by stop."""
    with _lock:
        return sorted(_index.get_routes_by_stop(stop_id))

def stops_by_route(route_id: str) -> List[str]:
    """Returns the stops by route."""
    with _lock:
        return sorted(_index.get_stops_by_route(route_id))

def all_routes() -> List[str]:
    """Returns all routes."""
    with _lock:
        return sorted(_index.stops_by_route.keys())

def all_stops() -> List[str]:
    """Returns all stops."""
    with _lock:
        return sorted(_index.routes_by_stop.keys())

def routes_with_stops() -> dict[str, list[str]]:
    """Returns the routes with stops."""
    with _lock:
        # We return a sorted copy to not expose mutable internal references
        return {rid: sorted(stops) for rid, stops in _index.stops_by_route.items()}
