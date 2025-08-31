from __future__ import annotations
from datetime import datetime, timezone, timedelta
from pathlib import Path

from app.schemas.analytics import (
    TopCustomersRequest, TopCustomersResponse, TopCustomerItem
)
from app.algorithms.top_customers import (
    iter_csv_transactions, top_k_exact, top_k_from_file_two_pass
)

def top_customers_service(req: TopCustomersRequest) -> TopCustomersResponse:
    """
    Computes the top customers based on the transactions dataset.
    Args:
        req: TopCustomersRequest
    Returns:
        TopCustomersResponse
    """
    # Temporal window -> epoch
    if req.days is not None:
        end_datetime_utc = datetime.now(timezone.utc)
        start_datetime_utc = end_datetime_utc - timedelta(days=req.days)
    else:
        start_datetime_utc = req.start
        end_datetime_utc = req.end
        if start_datetime_utc.tzinfo is None: start_datetime_utc = start_datetime_utc.replace(tzinfo=timezone.utc)
        if end_datetime_utc.tzinfo is None:   end_datetime_utc = end_datetime_utc.replace(tzinfo=timezone.utc)

    start_timestamp = int(start_datetime_utc.timestamp())
    end_timestamp = int(end_datetime_utc.timestamp())
    path = Path(req.path)

    if req.mode == "exact":
        pairs = top_k_exact(iter_csv_transactions(path), start_timestamp, end_timestamp, req.top_customers)
        used = "exact"
    elif req.mode == "stream":
        pairs = top_k_from_file_two_pass(path, start_timestamp, end_timestamp, req.top_customers, req.capacity)
        used = "stream"
    else:
        # Simple heuristic by file size
        size = path.stat().st_size if path.exists() else 0
        if size > 300 * 1024 * 1024:
            pairs = top_k_from_file_two_pass(path, start_timestamp, end_timestamp, req.top_customers, req.capacity)
            used = "stream"
        else:
            pairs = top_k_exact(iter_csv_transactions(path), start_timestamp, end_timestamp, req.top_customers)
            used = "exact"

    items = [TopCustomerItem(customer_id=cid, count=cnt) for cid, cnt in pairs]
    return TopCustomersResponse(
        start_timestamp=start_timestamp, end_timestamp=end_timestamp, top_customers=req.top_customers, mode=used, results=items
    )
