from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from .value_objects import Money, OperationType, CategoryType, parse_iso_date


@dataclass(slots=True)
class BankAccount:
    id: str
    name: str
    balance: Money = field(default_factory=lambda: Money.of(0))

    def apply(self, operation_type: OperationType, amount: Money) -> None:
        if operation_type == OperationType.INCOME:
            self.balance = self.balance + amount
        else:
            self.balance = self.balance - amount


@dataclass(slots=True, frozen=True)
class Category:
    id: str
    type: CategoryType
    name: str


@dataclass(slots=True)
class Operation:
    id: str
    type: OperationType
    bank_account_id: str
    amount: Money
    date: date
    description: Optional[str]
    category_id: str

    @classmethod
    def with_parsed_date(
        cls,
        *,
        id: str,
        type: OperationType,
        bank_account_id: str,
        amount: Money,
        date_value,
        description: Optional[str],
        category_id: str,
    ) -> "Operation":
        return cls(
            id=id,
            type=type,
            bank_account_id=bank_account_id,
            amount=amount,
            date=parse_iso_date(date_value),
            description=description,
            category_id=category_id,
        )
