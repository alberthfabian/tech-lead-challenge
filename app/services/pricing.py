from app.schemas.order import OrderRequest, OrderResponse, Stratum
from app.core.config import settings

# regla simple: el envío baja para estratos más altos (ejemplo)
_STRATUM_MULTIPLIER = {
    Stratum.UNO: 0.8, Stratum.DOS: 0.9, Stratum.TRES: 1.0,
    Stratum.CUATRO: 1.1, Stratum.CINCO: 1.2, Stratum.SEIS: 1.3,
}

def compute_order_total(req: OrderRequest) -> OrderResponse:
    subtotal = sum(it.price * it.quantity for it in req.items)

    base = settings.delivery_base_fee
    shipping = round(base * _STRATUM_MULTIPLIER[req.stratum])

    discount = 0
    if subtotal >= settings.discount_threshold:
        discount = round(subtotal * settings.discount_rate)

    total = max(0, subtotal + shipping - discount)
    return OrderResponse(subtotal=subtotal, shipping=shipping, discount=discount, total=total)
