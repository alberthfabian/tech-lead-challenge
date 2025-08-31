from __future__ import annotations
import csv, gzip, heapq
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Tuple

Transaction = Tuple[int, str, int]  # (timestamp, customer_id, amount)

# ---------------------------
# CSV reading utilities
# ---------------------------
def _open_in(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt", newline="", encoding="utf-8")
    return open(path, "r", newline="", encoding="utf-8")

def iter_csv_transactions(path: Path) -> Iterator[Transaction]:
    with _open_in(path) as f:
        r = csv.DictReader(f)
        for row in r:
            yield (int(row["timestamp"]), row["customer_id"], int(row["amount"]))

# ---------------------------
# Mode 1: EXACT (memory)
# ---------------------------
def top_k_exact(
    rows: Iterable[Transaction], start_timestamp: int, end_timestamp: int, k: int = 10
) -> List[Tuple[str, int]]:
    c = Counter()
    for ts, cid, _ in rows:
        if start_timestamp <= ts <= end_timestamp:
            c[cid] += 1
    # O(m log k) with nlargest (m = unique customers)
    return heapq.nlargest(k, c.items(), key=lambda x: x[1])

# ---------------------------
# Mode 2: STREAMING (Misra–Gries + verification)
# ---------------------------
@dataclass
class MG:
    capacity: int
    counters: Dict[str, int]

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.counters = {}

    def offer(self, key: str):
        if key in self.counters:
            self.counters[key] += 1
        elif len(self.counters) < self.capacity:
            self.counters[key] = 1
        else:
            # global decrement: O(b)
            to_del = []
            for k in self.counters:
                self.counters[k] -= 1
                if self.counters[k] == 0:
                    to_del.append(k)
            for k in to_del:
                del self.counters[k]

def top_k_streaming_two_pass(
    rows: Iterable[Transaction],
    start_timestamp: int,
    end_timestamp: int,
    top_customers: int = 10,
    capacity: int = 200,  # bounded memory (adjustable)
) -> List[Tuple[str, int]]:
    # 1) Pass 1: candidates with Misra–Gries
    mg = MG(capacity=capacity)
    for ts, cid, _ in rows:
        if start_timestamp <= ts <= end_timestamp:
            mg.offer(cid)

    candidates = set(mg.counters.keys())
    # 2) Pass 2: exact count ONLY of candidates
    counts: Dict[str, int] = {c: 0 for c in candidates}
    # rows puede ser generador de 1 sola pasada; documenta que para archivo se itera 2 veces
    if hasattr(rows, "__iter__") and not hasattr(rows, "__next__"):
        iterable = rows  # podría ser lista
    # For security, we require new reading if it was a generator
    # (in CLI we will read twice from file)
    for ts, cid, _ in rows:
        if start_timestamp <= ts <= end_timestamp and cid in counts:
            counts[cid] += 1

    return heapq.nlargest(top_customers, counts.items(), key=lambda x: x[1])

# Helper for file in 2 passes
def top_k_from_file_two_pass(path: Path, start_timestamp: int, end_timestamp: int, top_customers: int = 10, capacity: int = 200):
    # pass 1
    mg = MG(capacity=capacity)
    for ts, cid, _ in iter_csv_transactions(path):
        if start_timestamp <= ts <= end_timestamp:
            mg.offer(cid)
    candidates = set(mg.counters.keys())

    # pass 2
    counts: Dict[str, int] = {c: 0 for c in candidates}
    for ts, cid, _ in iter_csv_transactions(path):
        if start_timestamp <= ts <= end_timestamp and cid in counts:
            counts[cid] += 1
    return heapq.nlargest(top_customers, counts.items(), key=lambda x: x[1])
