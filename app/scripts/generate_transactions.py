import csv, gzip, random, time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable
import typer
from faker import Faker
from tqdm import tqdm

app = typer.Typer(help="Generador de dataset de transacciones")

def _open_out(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "wt", newline="", encoding="utf-8")
    return open(path, "w", newline="", encoding="utf-8")

def heavy_tail_weights(n_customers: int, s: float = 1.1) -> list[float]:
    # Distribución Zipf-like: más realista para e-commerce
    return [1 / ((i + 1) ** s) for i in range(n_customers)]

@app.command()
def make(
    out: Path = typer.Argument(Path("/app/data/transactions.csv.gz")),
    rows: int = typer.Option(1_000_000, help="Filas a generar"),
    customers: int = typer.Option(100_000, help="Clientes únicos"),
    days: int = typer.Option(90, help="Rango de días hacia atrás"),
    min_amount: int = typer.Option(5000),
    max_amount: int = typer.Option(500_000),
):
    fake = Faker()
    start = datetime.utcnow() - timedelta(days=days)
    weights = heavy_tail_weights(customers, s=1.07)
    customer_ids = [f"C{str(i).zfill(6)}" for i in range(customers)]

    with _open_out(out) as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "customer_id", "amount"])
        for _ in tqdm(range(rows), desc="generating"):
            # timestamp aleatorio en [start, now]
            dt = start + timedelta(seconds=random.randint(0, days * 24 * 3600))
            ts = int(dt.timestamp())
            cid = random.choices(customer_ids, weights=weights, k=1)[0]
            # monto con sesgo (picos bajos + outliers)
            base = random.randint(min_amount, max_amount)
            amount = int(base * random.choice([0.9, 1.0, 1.1, 1.25, 0.75, 1.5]))
            w.writerow([ts, cid, amount])

    typer.echo(f"OK -> {out}")

if __name__ == "__main__":
    app()
