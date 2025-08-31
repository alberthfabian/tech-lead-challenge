from typing import List, Dict
from pydantic import BaseModel, Field

class CreateRouteRequest(BaseModel):
    """
    Request to create a new route.
    """
    route_id: str = Field(..., min_length=1)
    stops: List[str] = Field(default_factory=list)

class StopMutationRequest(BaseModel):
    """
    Request to add or remove a stop from a route.
    """
    stop_id: str = Field(..., min_length=1)

class RoutesByStopResponse(BaseModel):
    """
    Response to get the routes by stop.
    """
    stop_id: str
    routes: List[str]

class StopsByRouteResponse(BaseModel):
    """
    Response to get the stops by route.
    """
    route_id: str
    stops: List[str]

class OkResponse(BaseModel):
    """
    Response to indicate that the request was successful.
    """
    ok: bool = True

class AllRoutesResponse(BaseModel):
    """
    Response to get all routes.
    """
    routes: List[str]

class AllStopsResponse(BaseModel):
    """
    Response to get all stops.
    """
    stops: List[str]

class RoutesWithStopsResponse(BaseModel):
    """
    Response to get the routes with stops.
    """
    routes: Dict[str, List[str]]