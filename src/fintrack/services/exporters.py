from __future__ import annotations
import csv
import io
import json
from pathlib import Path
from typing import Iterable, Protocol
from ..domain.entities import BankAccount, Category, Operation

class ExportVisitor(Protocol):
    def visit_account(self, a: BankAccount) -> None: ...
    def visit_category(self, c: Category) -> None: ...
    def visit_operation(self, o: Operation) -> None: ...
    def result(self) -> object: ...


class DataSnapshot:
    def __init__(
        self,
        accounts: Iterable[BankAccount],
        categories: Iterable[Category],
        operations: Iterable[Operation],
    ) -> None:
        self.accounts = list(accounts)
        self.categories = list(categories)
        self.operations = list(operations)

    def accept(self, visitor: ExportVisitor) -> object:
        for a in self.accounts:
            visitor.visit_account(a)
        for c in self.categories:
            visitor.visit_category(c)
        for o in self.operations:
            visitor.visit_operation(o)
        return visitor.result()


class JsonExportVisitor:
    def __init__(self) -> None:
        self._data = {"accounts": [], "categories": [], "operations": []}

    def visit_account(self, a: BankAccount) -> None:
        self._data["accounts"].append(
            {"id": a.id, "name": a.name, "balance": a.balance.as_str()})

    def visit_category(self, c: Category) -> None:
        self._data["categories"].append(
            {"id": c.id, "type": c.type.value, "name": c.name})

    def visit_operation(self, o: Operation) -> None:
        self._data["operations"].append(
            {
                "id": o.id,
                "type": o.type.value,
                "bank_account_id": o.bank_account_id,
                "amount": o.amount.as_str(),
                "date": o.date.isoformat(),
                "description": o.description,
                "category_id": o.category_id,
            }
        )

    def result(self) -> str:
        return json.dumps(self._data, ensure_ascii=False, indent=2)


class YamlExportVisitor(JsonExportVisitor):
    def result(self) -> str:
        try:
            import yaml
        except Exception:
            data = json.loads(super().result())
            return "---\n" + "\n".join(
                [
                    "accounts:",
                    *[f"  - id: {a['id']}\n    name: {a['name']}\n    balance: {a['balance']}" for a in data["accounts"]],
                    "categories:",
                    *[f"  - id: {c['id']}\n    type: {c['type']}\n    name: {c['name']}" for c in data["categories"]],
                    "operations:",
                    *[
                        "  - id: {id}\n    type: {type}\n    bank_account_id: {bank_account_id}\n"
                        "    amount: {amount}\n    date: {date}\n    description: {description}\n    category_id: {category_id}".format(
                            **o
                        )
                        for o in data["operations"]
                    ],
                ]
            )
        return yaml.safe_dump(
            json.loads(
                super().result()),
            sort_keys=False,
            allow_unicode=True)


class CsvExportVisitor:
    def __init__(self) -> None:
        self._acc = io.StringIO()
        self._cat = io.StringIO()
        self._ops = io.StringIO()
        self._acc_writer = csv.DictWriter(
            self._acc, fieldnames=[
                "id", "name", "balance"])
        self._cat_writer = csv.DictWriter(
            self._cat, fieldnames=[
                "id", "type", "name"])
        self._ops_writer = csv.DictWriter(
            self._ops,
            fieldnames=[
                "id",
                "type",
                "bank_account_id",
                "amount",
                "date",
                "description",
                "category_id"],
        )
        self._acc_writer.writeheader()
        self._cat_writer.writeheader()
        self._ops_writer.writeheader()

    def visit_account(self, a: BankAccount) -> None:
        self._acc_writer.writerow(
            {"id": a.id, "name": a.name, "balance": a.balance.as_str()})

    def visit_category(self, c: Category) -> None:
        self._cat_writer.writerow(
            {"id": c.id, "type": c.type.value, "name": c.name})

    def visit_operation(self, o: Operation) -> None:
        self._ops_writer.writerow(
            {
                "id": o.id,
                "type": o.type.value,
                "bank_account_id": o.bank_account_id,
                "amount": o.amount.as_str(),
                "date": o.date.isoformat(),
                "description": o.description or "",
                "category_id": o.category_id,
            }
        )

    def result(self) -> dict[str, str]:
        return {
            "accounts.csv": self._acc.getvalue(),
            "categories.csv": self._cat.getvalue(),
            "operations.csv": self._ops.getvalue(),
        }


class ExportFacade:
    def __init__(self) -> None:
        pass

    def export_all(
        self,
        snapshot: DataSnapshot,
        *,
        fmt: str,
        target: str | Path,
    ) -> list[Path]:
        fmt = fmt.lower()
        out_paths: list[Path] = []
        if fmt == "json":
            res = snapshot.accept(JsonExportVisitor())
            path = Path(target)
            path.write_text(res, encoding="utf-8")
            out_paths.append(path)
        elif fmt == "yaml":
            res = snapshot.accept(YamlExportVisitor())
            path = Path(target)
            path.write_text(res, encoding="utf-8")
            out_paths.append(path)
        elif fmt == "csv":
            data = snapshot.accept(CsvExportVisitor())
            target_dir = Path(target)
            target_dir.mkdir(parents=True, exist_ok=True)
            for name, content in data.items():
                p = target_dir / name
                p.write_text(content, encoding="utf-8")
                out_paths.append(p)
        else:
            raise ValueError("Unsupported export format.")
        return out_paths
