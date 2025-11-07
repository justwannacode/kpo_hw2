from __future__ import annotations
from typing import Iterable, Optional
from datetime import date
from ..domain.entities import BankAccount, Category, Operation
from ..domain.value_objects import Money, CategoryType, OperationType
from .db import Database

def _row_to_account(row) -> BankAccount:
    return BankAccount(
        id=row["id"],
        name=row["name"],
        balance=Money.of(
            row["balance"]))


def _row_to_category(row) -> Category:
    return Category(
        id=row["id"],
        type=CategoryType(
            row["type"]),
        name=row["name"])


def _row_to_operation(row) -> Operation:
    return Operation.with_parsed_date(
        id=row["id"],
        type=OperationType(row["type"]),
        bank_account_id=row["bank_account_id"],
        amount=Money.of(row["amount"]),
        date_value=row["date"],
        description=row["description"],
        category_id=row["category_id"],
    )


class SqlBankAccountRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def add(self, account: BankAccount) -> None:
        self.db.execute(
            "INSERT INTO bank_accounts(id, name, balance) VALUES(?,?,?)",
            (account.id, account.name, account.balance.as_str()),
        )

    def update(self, account: BankAccount) -> None:
        self.db.execute(
            "UPDATE bank_accounts SET name=?, balance=? WHERE id=?",
            (account.name, account.balance.as_str(), account.id),
        )

    def delete(self, account_id: str) -> None:
        self.db.execute("DELETE FROM bank_accounts WHERE id=?", (account_id,))

    def get(self, account_id: str) -> Optional[BankAccount]:
        rows = self.db.query(
            "SELECT * FROM bank_accounts WHERE id=?", (account_id,))
        return _row_to_account(rows[0]) if rows else None

    def list_all(self) -> Iterable[BankAccount]:
        rows = self.db.query("SELECT * FROM bank_accounts ORDER BY name")
        return [_row_to_account(r) for r in rows]


class SqlCategoryRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def add(self, category: Category) -> None:
        self.db.execute(
            "INSERT INTO categories(id, type, name) VALUES(?,?,?)",
            (category.id, category.type.value, category.name),
        )

    def update(self, category: Category) -> None:
        self.db.execute(
            "UPDATE categories SET type=?, name=? WHERE id=?",
            (category.type.value, category.name, category.id),
        )

    def delete(self, category_id: str) -> None:
        self.db.execute("DELETE FROM categories WHERE id=?", (category_id,))

    def get(self, category_id: str) -> Optional[Category]:
        rows = self.db.query(
            "SELECT * FROM categories WHERE id=?", (category_id,))
        return _row_to_category(rows[0]) if rows else None

    def list_all(self) -> Iterable[Category]:
        rows = self.db.query("SELECT * FROM categories ORDER BY name")
        return [_row_to_category(r) for r in rows]

    def list_by_type(self, type_: str) -> Iterable[Category]:
        rows = self.db.query(
            "SELECT * FROM categories WHERE type=? ORDER BY name", (type_,))
        return [_row_to_category(r) for r in rows]


class SqlOperationRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def add(self, operation: Operation) -> None:
        self.db.execute(
            """
            INSERT INTO operations(id, type, bank_account_id, amount, date, description, category_id)
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                operation.id,
                operation.type.value,
                operation.bank_account_id,
                operation.amount.as_str(),
                operation.date.isoformat(),
                operation.description,
                operation.category_id,
            ),
        )

    def delete(self, operation_id: str) -> None:
        self.db.execute("DELETE FROM operations WHERE id=?", (operation_id,))

    def get(self, operation_id: str) -> Optional[Operation]:
        rows = self.db.query(
            "SELECT * FROM operations WHERE id=?", (operation_id,))
        return _row_to_operation(rows[0]) if rows else None

    def list_all(self) -> Iterable[Operation]:
        rows = self.db.query(
            "SELECT * FROM operations ORDER BY date DESC, id DESC")
        return [_row_to_operation(r) for r in rows]

    def list_by_account(self, account_id: str) -> Iterable[Operation]:
        rows = self.db.query(
            "SELECT * FROM operations WHERE bank_account_id=? ORDER BY date DESC, id DESC",
            (account_id,
             ))
        return [_row_to_operation(r) for r in rows]

    def list_by_period(
            self,
            date_from: date,
            date_to: date) -> Iterable[Operation]:
        rows = self.db.query(
            "SELECT * FROM operations WHERE date BETWEEN ? AND ? ORDER BY date",
            (date_from.isoformat(), date_to.isoformat()),
        )
        return [_row_to_operation(r) for r in rows]
