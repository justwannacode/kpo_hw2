from __future__ import annotations
from typing import Iterable, Optional
from ..domain.entities import BankAccount, Category, Operation
from ..domain.value_objects import Money, OperationType, CategoryType
from ..domain.repositories import BankAccountRepository, CategoryRepository, OperationRepository
from ..domain.factories import EntityFactory


class AccountFacade:
    def __init__(self, accounts: BankAccountRepository,
                 factory: EntityFactory) -> None:
        self._accounts = accounts
        self._factory = factory

    def create(self, name: str, initial_balance: Money) -> BankAccount:
        acc = self._factory.create_account(name, initial_balance)
        self._accounts.add(acc)
        return acc

    def update(self, account_id: str, *, name: str |
               None = None) -> Optional[BankAccount]:
        acc = self._accounts.get(account_id)
        if not acc:
            return None
        acc = self._factory.update_account(acc, name=name)
        self._accounts.update(acc)
        return acc

    def delete(self, account_id: str) -> None:
        self._accounts.delete(account_id)

    def get(self, account_id: str) -> Optional[BankAccount]:
        return self._accounts.get(account_id)

    def list(self) -> Iterable[BankAccount]:
        return self._accounts.list_all()

    def recalc_balance(
            self,
            operations: Iterable[Operation],
            account_id: str) -> Optional[BankAccount]:
        acc = self._accounts.get(account_id)
        if not acc:
            return None
        from decimal import Decimal
        total = Decimal("0.00")
        for op in operations:
            if op.bank_account_id != account_id:
                continue
            amt = op.amount.amount
            total += amt if op.type == OperationType.INCOME else -amt
        acc.balance = Money.of(total)
        self._accounts.update(acc)
        return acc


class CategoryFacade:
    def __init__(self, categories: CategoryRepository,
                 factory: EntityFactory) -> None:
        self._categories = categories
        self._factory = factory

    def create(self, type_: CategoryType, name: str) -> Category:
        cat = self._factory.create_category(type_, name)
        self._categories.add(cat)
        return cat

    def update(self, category_id: str, *, new_name: str | None = None,
               new_type: CategoryType | None = None) -> Optional[Category]:
        cat = self._categories.get(category_id)
        if not cat:
            return None
        if new_name is not None:
            cat = Category(id=cat.id, type=cat.type, name=new_name)
        if new_type is not None:
            cat = Category(id=cat.id, type=new_type, name=cat.name)
        self._categories.update(cat)
        return cat

    def delete(self, category_id: str) -> None:
        self._categories.delete(category_id)

    def get(self, category_id: str) -> Optional[Category]:
        return self._categories.get(category_id)

    def list(self) -> Iterable[Category]:
        return self._categories.list_all()

    def list_by_type(self, type_: CategoryType) -> Iterable[Category]:
        return self._categories.list_by_type(type_.value)


class OperationFacade:
    def __init__(
            self,
            accounts: AccountFacade,
            categories: CategoryFacade,
            operations: OperationRepository,
            factory: EntityFactory) -> None:
        self._accounts = accounts
        self._categories = categories
        self._operations = operations
        self._factory = factory

    def add(
        self,
        *,
        type_: OperationType,
        bank_account_id: str,
        amount: Money,
        date_value,
        description: str | None,
        category_id: str,
    ) -> Optional[Operation]:
        acc = self._accounts.get(bank_account_id)
        cat = self._categories.get(category_id)
        if not acc or not cat:
            return None
        op = self._factory.create_operation(
            type_=type_,
            bank_account_id=bank_account_id,
            amount=amount,
            date_value=date_value,
            description=description,
            category_id=category_id,
            category_type=cat.type,
        )
        # применяем к счету и сохраняем обе сущности
        acc.apply(op.type, op.amount)
        self._accounts._accounts.update(acc)
        self._operations.add(op)
        return op

    def delete(self, operation_id: str) -> None:
        self._operations.delete(operation_id)

    def list_all(self) -> Iterable[Operation]:
        return self._operations.list_all()

    def list_by_account(self, account_id: str) -> Iterable[Operation]:
        return self._operations.list_by_account(account_id)
