from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Protocol, Any, Callable


class Command(Protocol):
    def execute(self) -> Any: ...


@dataclass
class StatsCollector:
    durations: dict[str, list[float]] = field(default_factory=dict)

    def record(self, name: str, duration_s: float) -> None:
        self.durations.setdefault(name, []).append(duration_s)

    def summary(self) -> dict[str, float]:
        return {name: sum(vals) / len(vals)
                for name, vals in self.durations.items() if vals}


@dataclass
class TimedCommandDecorator:
    name: str
    command: Command
    stats: StatsCollector

    def execute(self):
        start = time.perf_counter()
        try:
            return self.command.execute()
        finally:
            elapsed = time.perf_counter() - start
            self.stats.record(self.name, elapsed)


def measure_time(fn: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            dt = time.perf_counter() - t0
            print(f"[time] {fn.__name__} took {dt:.4f}s")
    return wrapper
