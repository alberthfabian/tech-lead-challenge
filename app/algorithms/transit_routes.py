# app/algorithms/transit_routes.py
from typing import Dict, Set, Iterable, List

class TransitIndex:
    """
    Índice de rutas de transporte público con consultas O(1) promedio.
    Estructura:
      - stops_by_route[route_id] -> {stop_id, ...}
      - routes_by_stop[stop_id]  -> {route_id, ...}
    """

    def __init__(self):
        self.stops_by_route: Dict[str, Set[str]] = {}
        self.routes_by_stop: Dict[str, Set[str]] = {}

    # ----- Lectura -----
    def get_routes_by_stop(self, stop_id: str) -> Set[str]:
        return set(self.routes_by_stop.get(stop_id, set()))

    def get_stops_by_route(self, route_id: str) -> Set[str]:
        return set(self.stops_by_route.get(route_id, set()))

    # ----- Mutación -----
    def add_route(self, route_id: str, stops: Iterable[str]) -> None:
        stops_set = set(stops)
        self.stops_by_route[route_id] = stops_set
        for stop_id in stops_set:
            self.routes_by_stop.setdefault(stop_id, set()).add(route_id)

    def add_stop_to_route(self, route_id: str, stop_id: str) -> None:
        self.stops_by_route.setdefault(route_id, set()).add(stop_id)
        self.routes_by_stop.setdefault(stop_id, set()).add(route_id)

    def remove_stop_from_route(self, route_id: str, stop_id: str) -> None:
        if route_id in self.stops_by_route and stop_id in self.stops_by_route[route_id]:
            self.stops_by_route[route_id].remove(stop_id)
            if not self.stops_by_route[route_id]:
                # Si la ruta quedó vacía, opcionalmente eliminarla
                del self.stops_by_route[route_id]
        if stop_id in self.routes_by_stop and route_id in self.routes_by_stop[stop_id]:
            self.routes_by_stop[stop_id].remove(route_id)
            if not self.routes_by_stop[stop_id]:
                del self.routes_by_stop[stop_id]

    def remove_route(self, route_id: str) -> None:
        stops = list(self.stops_by_route.get(route_id, []))
        for stop_id in stops:
            self.routes_by_stop[stop_id].discard(route_id)
            if not self.routes_by_stop[stop_id]:
                del self.routes_by_stop[stop_id]
        self.stops_by_route.pop(route_id, None)
