from fastapi import APIRouter, HTTPException, status
from app.schemas.order import OrderRequest, OrderResponse
from app.services.pricing import compute_order_total

from app.schemas.analytics import TopCustomersRequest, TopCustomersResponse
from app.services.analytics import top_customers_service

from app.schemas.dataset import DatasetGenRequest, DatasetGenResponse
from app.services.dataset import generate_transactions_dataset

from app.schemas.transit import (
    CreateRouteRequest, StopMutationRequest,
    RoutesByStopResponse, StopsByRouteResponse, OkResponse
)
from app.services.transit import (
    create_route, add_stop, remove_stop, delete_route,
    routes_by_stop, stops_by_route
)
from app.schemas.transit import (
    AllRoutesResponse, AllStopsResponse, RoutesWithStopsResponse,
)

from app.services.transit import (
    all_routes, all_stops, routes_with_stops,
)

router = APIRouter(tags=["orders", "analytics"])


# 1. Data algorithms and structures
# 1.1. Question 1: Complexity and optimization
@router.post("/analytics/top-customers", response_model=TopCustomersResponse)
def top_customers(payload: TopCustomersRequest):
    try:
        return top_customers_service(payload)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Archivo de datos no encontrado")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# 1.1.1. Generate transactions dataset
@router.post("/datasets/transactions/generate", response_model=DatasetGenResponse)
def dataset_generate(payload: DatasetGenRequest):
    try:
        return generate_transactions_dataset(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# 1.2. Question 2: Data structures
@router.post("/transit/routes", response_model=OkResponse, tags=["transit"])
def api_create_route(payload: CreateRouteRequest):
    created = create_route(payload.route_id, payload.stops)
    if not created:
        # Duplicate: already exists that route
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Route already exists",
        )
    return OkResponse()

@router.get("/transit/routes/{route_id}/stops", response_model=StopsByRouteResponse, tags=["transit"])
def api_stops_by_route(route_id: str):
    return StopsByRouteResponse(route_id=route_id, stops=stops_by_route(route_id))

@router.post("/transit/routes/{route_id}/stops", response_model=OkResponse, tags=["transit"])
def api_add_stop(route_id: str, payload: StopMutationRequest):
    created = add_stop(route_id, payload.stop_id)
    if not created:
        # Duplicate: already exists that stop on the route
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Stop already exists on this route",
        )
    return OkResponse()

@router.delete("/transit/routes/{route_id}/stops/{stop_id}", response_model=OkResponse, tags=["transit"])
def api_remove_stop(route_id: str, stop_id: str):
    remove_stop(route_id, stop_id)
    return OkResponse()

@router.get("/transit/stops/{stop_id}/routes", response_model=RoutesByStopResponse, tags=["transit"])
def api_routes_by_stop(stop_id: str):
    return RoutesByStopResponse(stop_id=stop_id, routes=routes_by_stop(stop_id))

@router.delete("/transit/routes/{route_id}", response_model=OkResponse, tags=["transit"])
def api_delete_route(route_id: str):
    delete_route(route_id)
    return OkResponse()

@router.get("/transit/routes", response_model=AllRoutesResponse, tags=["transit"])
def api_all_routes():
    return AllRoutesResponse(routes=all_routes())

@router.get("/transit/stops", response_model=AllStopsResponse, tags=["transit"])
def api_all_stops():
    return AllStopsResponse(stops=all_stops())

@router.get("/transit/routes-with-stops", response_model=RoutesWithStopsResponse, tags=["transit"])
def api_routes_with_stops():
    return RoutesWithStopsResponse(routes=routes_with_stops())


# 2. Design and architecture

    

# 3. Coding and resolution of problems
@router.post("/orders/quote", response_model=OrderResponse)
def quote_order(payload: OrderRequest):
    try:
        return compute_order_total(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))