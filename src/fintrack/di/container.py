from __future__ import annotations
from dataclasses import dataclass
from ..infrastructure.db import Database
from ..infrastructure.repositories_sql import (
    SqlBankAccountRepository,
    SqlCategoryRepository,
    SqlOperationRepository,
)
from ..infrastructure.proxies import (
    CachedBankAccountRepository,
    CachedCategoryRepository,
    WriteThroughOperationRepository,
)
from ..domain.factories import EntityFactory
from ..services.facades import AccountFacade, CategoryFacade, OperationFacade
from ..services.analytics import AnalyticsService
from ..services.exporters import ExportFacade
from ..services.importers import JsonImporter, YamlImporter, CsvImporter


@dataclass
class Container:
    db_path: str = ":memory:"

    def __post_init__(self) -> None:
        # infrastructure
        self.db = Database(self.db_path)
        acc_sql = SqlBankAccountRepository(self.db)
        cat_sql = SqlCategoryRepository(self.db)
        op_sql = SqlOperationRepository(self.db)

        # proxies
        self.accounts_repo = CachedBankAccountRepository(acc_sql)
        self.categories_repo = CachedCategoryRepository(cat_sql)
        self.operations_repo = WriteThroughOperationRepository(op_sql)

        # domain
        self.factory = EntityFactory()

        # facades
        self.accounts = AccountFacade(self.accounts_repo, self.factory)
        self.categories = CategoryFacade(self.categories_repo, self.factory)
        self.operations = OperationFacade(
            self.accounts,
            self.categories,
            self.operations_repo,
            self.factory)

        # services
        self.analytics = AnalyticsService()
        self.export = ExportFacade()

        # importers
        self.import_json = JsonImporter(
            self.factory,
            self.accounts,
            self.categories,
            self.operations)
        self.import_yaml = YamlImporter(
            self.factory,
            self.accounts,
            self.categories,
            self.operations)
        self.import_csv = CsvImporter(
            self.factory,
            self.accounts,
            self.categories,
            self.operations)
