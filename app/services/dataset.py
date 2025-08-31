"""
Generates a transactions dataset with realistic data for the e-commerce business model.
The generated data includes:
- ID de cliente
- Customer name
- Customer city
- Customer email
"""
from __future__ import annotations
import csv, gzip, random, unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Tuple
from faker import Faker
from app.schemas.dataset import DatasetGenRequest, DatasetGenResponse

# -----------------------------
# Semantic constants
# -----------------------------
SECONDS_PER_DAY: int = 24 * 60 * 60
DEFAULT_HEAVY_TAIL_SKEW: float = 1.07
AMOUNT_VARIATION_FACTORS: Tuple[float, ...] = (0.75, 0.9, 1.0, 1.1, 1.25, 1.5)
CSV_HEADERS: Tuple[str, ...] = ("timestamp", "customer_id", "amount", "customer_name", "customer_city", "customer_email")

# -----------------------------
# Utilities
# -----------------------------
def _open_out(path: Path, compress_gzip: bool):
    """
    Opens a file for writing, with or without gzip compression.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if compress_gzip:
        return gzip.open(path, "wt", newline="", encoding="utf-8")
    return open(path, "w", newline="", encoding="utf-8")

def _heavy_tail_weights(total_customers: int, skew: float = DEFAULT_HEAVY_TAIL_SKEW) -> List[float]:
    """
    Zipf-like distribution: few customers concentrate more transactions.
    Simula heavy users (realista en e-commerce).
    """
    return [1 / ((index + 1) ** skew) for index in range(total_customers)]

def _slugify_for_email(name: str) -> str:
    """
    Converts 'María José Pérez' -> 'maria.jose.perez'
    (removes accents, replaces spaces with dots, filters rare characters)
    """
    nfkd = unicodedata.normalize("NFKD", name)
    no_accents = "".join([c for c in nfkd if not unicodedata.combining(c)])
    base = no_accents.lower().replace(" ", ".")
    safe = "".join(ch for ch in base if ch.isalnum() or ch in "._-")
    return safe.strip("._-") or "user"

def _build_customer_directory(
    customer_ids: List[str],
    faker: Faker,
) -> Dict[str, Tuple[str, str, str]]:
    """
    Creates an in-memory directory: customer_id -> (name, city, email)
    Guarantees consistency: the same id always has the same profile.
    """
    directory: Dict[str, Tuple[str, str, str]] = {}
    for cid in customer_ids:
        name = faker.name()
        city = faker.city()
        email_local = _slugify_for_email(name)
        email_domain = faker.free_email_domain()
        email = f"{email_local}@{email_domain}"
        directory[cid] = (name, city, email)
    return directory

# -----------------------------
# Main generator
# -----------------------------
def generate_transactions_dataset(request: DatasetGenRequest) -> DatasetGenResponse:
    """
    Generates a transactions dataset with realistic data for the e-commerce business model.
    The generated data includes:
    - ID de cliente
    - Customer name
    - Customer city
    - Customer email
    """
    if request.min_amount >= request.max_amount:
        raise ValueError("min_amount must be < max_amount")

    # Reproducibility
    if request.seed is not None:
        random.seed(request.seed)

    # Faker in es_CO for more realistic data in Colombia
    faker = Faker("es_CO")

    # Temporal window: now - days
    start_date_utc = datetime.now(timezone.utc) - timedelta(days=request.days)
    total_seconds_span = request.days * SECONDS_PER_DAY

    # Customers + probability distribution (heavy-tail)
    customer_ids = [f"C{str(customer_index).zfill(6)}" for customer_index in range(request.customers)]
    probability_weights = _heavy_tail_weights(request.customers)

    # Consistent directory of profiles by customer
    # (if the number of customers were huge and you worried about memory,
    #  we could change this to a "lazy" cache based on seed by cid)
    customer_directory = _build_customer_directory(customer_ids, faker)

    # Output
    output_path = Path(request.output_path)
    compress_gzip = bool(request.gzip or str(output_path).endswith(".gz"))

    with _open_out(output_path, compress_gzip) as file_handle:
        csv_writer = csv.writer(file_handle)
        csv_writer.writerow(CSV_HEADERS)

        # We write in streaming, without loading all rows to RAM
        for _ in range(request.rows):
            random_offset_seconds = random.randint(0, total_seconds_span)
            transaction_dt = start_date_utc + timedelta(seconds=random_offset_seconds)
            transaction_timestamp = int(transaction_dt.timestamp())

            customer_id = random.choices(customer_ids, weights=probability_weights, k=1)[0]
            customer_name, customer_city, customer_email = customer_directory[customer_id]

            base_amount = random.randint(request.min_amount, request.max_amount)
            variation_factor = random.choice(AMOUNT_VARIATION_FACTORS)
            final_amount = int(base_amount * variation_factor)

            csv_writer.writerow([
                transaction_timestamp,
                customer_id,
                final_amount,
                customer_name,
                customer_city,
                customer_email
            ])

    file_size_bytes = output_path.stat().st_size if output_path.exists() else 0
    return DatasetGenResponse(
        output_path=str(output_path),
        rows=request.rows,
        customers=request.customers,
        days=request.days,
        gzip=compress_gzip,
        size_bytes=file_size_bytes,
    )
