from __future__ import annotations
from dataclasses import dataclass
from ..domain.value_objects import Money, OperationType, CategoryType
from ..domain.entities import Operation, BankAccount, Category
from .facades import AccountFacade, CategoryFacade, OperationFacade

@dataclass
class CreateAccountCommand:
    facade: AccountFacade
    name: str
    initial_balance: Money

    def execute(self) -> BankAccount | None:
        return self.facade.create(self.name, self.initial_balance)


@dataclass
class UpdateAccountCommand:
    facade: AccountFacade
    account_id: str
    new_name: str | None = None

    def execute(self) -> BankAccount | None:
        return self.facade.update(self.account_id, name=self.new_name)


@dataclass
class DeleteAccountCommand:
    facade: AccountFacade
    account_id: str

    def execute(self) -> None:
        self.facade.delete(self.account_id)


@dataclass
class CreateCategoryCommand:
    facade: CategoryFacade
    type_: CategoryType
    name: str

    def execute(self) -> Category:
        return self.facade.create(self.type_, self.name)


@dataclass
class UpdateCategoryCommand:
    facade: CategoryFacade
    category_id: str
    new_name: str | None = None
    new_type: CategoryType | None = None

    def execute(self) -> Category | None:
        return self.facade.update(
            self.category_id,
            new_name=self.new_name,
            new_type=self.new_type)


@dataclass
class DeleteCategoryCommand:
    facade: CategoryFacade
    category_id: str

    def execute(self) -> None:
        self.facade.delete(self.category_id)


@dataclass
class AddOperationCommand:
    facade: OperationFacade
    type_: OperationType
    bank_account_id: str
    amount: Money
    date_value: str
    description: str | None
    category_id: str

    def execute(self) -> Operation | None:
        return self.facade.add(
            type_=self.type_,
            bank_account_id=self.bank_account_id,
            amount=self.amount,
            date_value=self.date_value,
            description=self.description,
            category_id=self.category_id,
        )


@dataclass
class DeleteOperationCommand:
    facade: OperationFacade
    operation_id: str

    def execute(self) -> None:
        self.facade.delete(self.operation_id)


@dataclass
class RecalculateAccountBalanceCommand:
    accounts: AccountFacade
    operations: OperationFacade
    account_id: str

    def execute(self):
        ops = self.operations.list_by_account(self.account_id)
        return self.accounts.recalc_balance(ops, self.account_id)
