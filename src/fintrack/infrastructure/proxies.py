from __future__ import annotations
from typing import Iterable, Optional
from .repositories_sql import SqlBankAccountRepository, SqlCategoryRepository, SqlOperationRepository
from ..domain.entities import BankAccount, Category, Operation
from ..domain.repositories import BankAccountRepository, CategoryRepository, OperationRepository

class CachedBankAccountRepository(BankAccountRepository):
    def __init__(self, repo: SqlBankAccountRepository) -> None:
        self._repo = repo
        self._cache: dict[str, BankAccount] = {
            a.id: a for a in repo.list_all()}

    def add(self, account: BankAccount) -> None:
        self._repo.add(account)
        self._cache[account.id] = account

    def update(self, account: BankAccount) -> None:
        self._repo.update(account)
        self._cache[account.id] = account

    def delete(self, account_id: str) -> None:
        self._repo.delete(account_id)
        self._cache.pop(account_id, None)

    def get(self, account_id: str) -> Optional[BankAccount]:
        return self._cache.get(account_id)

    def list_all(self) -> Iterable[BankAccount]:
        return list(self._cache.values())


class CachedCategoryRepository(CategoryRepository):
    def __init__(self, repo: SqlCategoryRepository) -> None:
        self._repo = repo
        self._cache: dict[str, Category] = {c.id: c for c in repo.list_all()}

    def add(self, category: Category) -> None:
        self._repo.add(category)
        self._cache[category.id] = category

    def update(self, category: Category) -> None:
        self._repo.update(category)
        self._cache[category.id] = category

    def delete(self, category_id: str) -> None:
        self._repo.delete(category_id)
        self._cache.pop(category_id, None)

    def get(self, category_id: str) -> Optional[Category]:
        return self._cache.get(category_id)

    def list_all(self) -> Iterable[Category]:
        return list(self._cache.values())

    def list_by_type(self, type_: str) -> Iterable[Category]:
        return [c for c in self._cache.values() if c.type.value == type_]


class WriteThroughOperationRepository(OperationRepository):
    # Кешируем только последний фрейм списка
    def __init__(self, repo: SqlOperationRepository) -> None:
        self._repo = repo
        self._snapshot: list[Operation] = list(repo.list_all())

    def add(self, operation: Operation) -> None:
        self._repo.add(operation)
        self._snapshot.insert(0, operation)

    def delete(self, operation_id: str) -> None:
        self._repo.delete(operation_id)
        self._snapshot = [op for op in self._snapshot if op.id != operation_id]

    def get(self, operation_id: str) -> Optional[Operation]:
        for op in self._snapshot:
            if op.id == operation_id:
                return op
        return self._repo.get(operation_id)

    def list_all(self) -> Iterable[Operation]:
        return list(self._snapshot)

    def list_by_account(self, account_id: str) -> Iterable[Operation]:
        return [op for op in self._snapshot if op.bank_account_id == account_id]

    def list_by_period(self, date_from, date_to) -> Iterable[Operation]:
        return [op for op in self._snapshot if date_from <= op.date <= date_to]
