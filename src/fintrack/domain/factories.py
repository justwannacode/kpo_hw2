from __future__ import annotations
import uuid
from dataclasses import replace
from .entities import BankAccount, Category, Operation
from .validators import BankAccountValidator, CategoryValidator, OperationValidator
from .value_objects import Money, OperationType, CategoryType


class EntityFactory:
    @staticmethod
    def new_id() -> str:
        return str(uuid.uuid4())

    def create_account(self, name: str, initial_balance: Money) -> BankAccount:
        BankAccountValidator.validate_create(name, initial_balance)
        return BankAccount(
            id=self.new_id(),
            name=name,
            balance=initial_balance)

    def update_account(self, account: BankAccount, *,
                       name: str | None = None) -> BankAccount:
        BankAccountValidator.validate_update(name)
        if name is not None:
            return replace(account, name=name)
        return account

    def create_category(self, type_: CategoryType, name: str) -> Category:
        CategoryValidator.validate_create(type_, name)
        return Category(id=self.new_id(), type=type_, name=name)

    def create_operation(
        self,
        *,
        type_: OperationType,
        bank_account_id: str,
        amount: Money,
        date_value,
        description: str | None,
        category_id: str,
        category_type: CategoryType,
    ) -> Operation:
        OperationValidator.validate_amount(amount)
        OperationValidator.validate_type_and_category(type_, category_type)
        return Operation.with_parsed_date(
            id=self.new_id(),
            type=type_,
            bank_account_id=bank_account_id,
            amount=amount,
            date_value=date_value,
            description=description,
            category_id=category_id,
        )
