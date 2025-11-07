from __future__ import annotations
import csv
import json
from pathlib import Path
from ..domain.value_objects import OperationType, CategoryType, Money
from ..domain.factories import EntityFactory
from .facades import AccountFacade, CategoryFacade, OperationFacade

class ImportErrorFormat(Exception):
    pass


class ImporterBase:
    def __init__(
            self,
            factory: EntityFactory,
            acc: AccountFacade,
            cat: CategoryFacade,
            ops: OperationFacade) -> None:
        self.factory = factory
        self.acc = acc
        self.cat = cat
        self.ops = ops

    def import_file(self, path: str | Path) -> None:
        data = self._parse(Path(path))
        self._persist(data)

    def _parse(self, path: Path) -> dict:
        raise NotImplementedError

    def _persist(self, data: dict) -> None:
        # ожидается структура {"accounts":[...], "categories":[...],
        # "operations":[...]}
        for a in data.get("accounts", []):
            self.acc.create(a["name"], Money.of(a.get("balance", "0")))
        cat_map: dict[str, str] = {}  # name->id для ссылок в operations
        for c in data.get("categories", []):
            cat = self.cat.create(CategoryType(c["type"]), c["name"])
            cat_map[c["name"]] = cat.id
        acc_map: dict[str, str] = {a.name: a.id for a in self.acc.list()}
        for o in data.get("operations", []):
            self.ops.add(
                type_=OperationType(o["type"]),
                bank_account_id=acc_map[o["account_name"]],
                amount=Money.of(o["amount"]),
                date_value=o["date"],
                description=o.get("description"),
                category_id=cat_map[o["category_name"]],
            )


class JsonImporter(ImporterBase):
    def _parse(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))


class YamlImporter(ImporterBase):
    def _parse(self, path: Path) -> dict:
        try:
            import yaml  # type: ignore
        except Exception as e:
            raise ImportErrorFormat(
                "PyYAML is required for YAML import.") from e
        return yaml.safe_load(path.read_text(encoding="utf-8"))


class CsvImporter(ImporterBase):
    """
    CSV-импорт ожидает три файла рядом с базовым путем:
    - {base}_accounts.csv (name,balance)
    - {base}_categories.csv (type,name)
    - {base}_operations.csv (type,account_name,amount,date,description,category_name)
    """
    def _parse(self, path: Path) -> dict:
        base = path.with_suffix("")
        data: dict = {"accounts": [], "categories": [], "operations": []}

        def read_csv(p: Path) -> list[dict]:
            if not p.exists():
                return []
            with p.open("r", encoding="utf-8", newline="") as f:
                return list(csv.DictReader(f))

        for row in read_csv(Path(str(base) + "_accounts.csv")):
            data["accounts"].append(
                {"name": row["name"], "balance": row.get("balance", "0")})

        for row in read_csv(Path(str(base) + "_categories.csv")):
            data["categories"].append(
                {"type": row["type"], "name": row["name"]})

        for row in read_csv(Path(str(base) + "_operations.csv")):
            data["operations"].append(
                {
                    "type": row["type"],
                    "account_name": row["account_name"],
                    "amount": row["amount"],
                    "date": row["date"],
                    "description": row.get("description") or None,
                    "category_name": row["category_name"],
                }
            )
        return data
