from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from enum import Enum
from datetime import date, datetime


class OperationType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class CategoryType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


@dataclass(slots=True, frozen=True)
class Money:
    amount: Decimal

    @staticmethod
    def _to_decimal(value: int | float | str | Decimal) -> Decimal:
        if isinstance(value, Decimal):
            return value
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"Invalid money value: {value}") from e

    @classmethod
    def of(cls, value: int | float | str | Decimal) -> "Money":
        d = cls._to_decimal(value).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP)
        return cls(d)

    def __add__(self, other: "Money") -> "Money":
        return Money.of(self.amount + other.amount)

    def __sub__(self, other: "Money") -> "Money":
        return Money.of(self.amount - other.amount)

    def __neg__(self) -> "Money":
        return Money.of(-self.amount)

    def __lt__(self, other: "Money") -> bool:  # For comparisons if needed
        return self.amount < other.amount

    def as_str(self) -> str:
        return format(self.amount, "f")


def parse_iso_date(value: str | date | datetime) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    return datetime.fromisoformat(value).date()
