from __future__ import annotations
from decimal import Decimal
from .value_objects import Money, OperationType, CategoryType


class ValidationError(Exception):
    pass


class BankAccountValidator:
    @staticmethod
    def validate_name(name: str) -> None:
        if not name or not name.strip():
            raise ValidationError("Account name must be non-empty.")

    @classmethod
    def validate_create(cls, name: str, balance: Money) -> None:
        cls.validate_name(name)
        if balance.amount < Decimal("0"):
            raise ValidationError("Initial balance cannot be negative.")

    @classmethod
    def validate_update(cls, name: str | None) -> None:
        if name is not None:
            cls.validate_name(name)


class CategoryValidator:
    @staticmethod
    def validate_name(name: str) -> None:
        if not name or not name.strip():
            raise ValidationError("Category name must be non-empty.")

    @classmethod
    def validate_create(cls, type_: CategoryType, name: str) -> None:
        if type_ not in (CategoryType.INCOME, CategoryType.EXPENSE):
            raise ValidationError("Invalid category type.")
        cls.validate_name(name)


class OperationValidator:
    @classmethod
    def validate_amount(cls, amount: Money) -> None:
        if amount.amount <= 0:
            raise ValidationError("Operation amount must be > 0.")

    @classmethod
    def validate_type_and_category(
            cls,
            op_type: OperationType,
            cat_type: CategoryType) -> None:
        if (op_type == OperationType.INCOME and cat_type != CategoryType.INCOME) or (
                op_type == OperationType.EXPENSE and cat_type != CategoryType.EXPENSE):
            raise ValidationError("Operation type must match category type.")
