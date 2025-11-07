from __future__ import annotations
from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Iterable
from ..domain.entities import Operation
from ..domain.value_objects import OperationType, Money


class AnalyticsService:
    def difference_by_period(
            self,
            operations: Iterable[Operation],
            date_from: date,
            date_to: date) -> Money:
        income = Decimal("0")
        expense = Decimal("0")
        for op in operations:
            if not (date_from <= op.date <= date_to):
                continue
            if op.type == OperationType.INCOME:
                income += op.amount.amount
            else:
                expense += op.amount.amount
        return Money.of(income - expense)

    def grouped_by_category(
            self, operations: Iterable[Operation]) -> dict[str, Money]:
        sums: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        for op in operations:
            key = op.category_id
            amt = op.amount.amount if op.type == OperationType.INCOME else -op.amount.amount
            sums[key] += amt
        return {k: Money.of(v) for k, v in sums.items()}
