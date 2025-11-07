from __future__ import annotations
from datetime import date

from ..di.container import Container
from ..domain.value_objects import Money, CategoryType, OperationType
from ..services.commands import (
    CreateAccountCommand,
    UpdateAccountCommand,
    DeleteAccountCommand,
    CreateCategoryCommand,
    DeleteCategoryCommand,
    UpdateCategoryCommand,
    AddOperationCommand,
    DeleteOperationCommand,
    RecalculateAccountBalanceCommand,
)
from ..services.decorators import StatsCollector, TimedCommandDecorator
from ..services.exporters import DataSnapshot


def prompt(msg: str) -> str:
    return input(msg).strip()


def pick(options: list[tuple[str, str]],
         title: str = "Выберите действие") -> str:
    print(f"\n=== {title} ===")
    for i, (code, label) in enumerate(options, start=1):
        print(f"{i}. {label}")
    while True:
        s = input("№: ").strip()
        if s.isdigit() and 1 <= int(s) <= len(options):
            return options[int(s) - 1][0]
        print("Неверный ввод, попробуйте снова.")


def show_accounts(c: Container):
    print("\nСчета:")
    for a in c.accounts.list():
        print(f"- {a.id} | {a.name} | balance={a.balance.as_str()}")


def show_categories(c: Container):
    print("\nКатегории:")
    for cat in c.categories.list():
        print(f"- {cat.id} | {cat.type.value} | {cat.name}")


def show_operations(c: Container):
    print("\nОперации:")
    for op in c.operations.list_all():
        base = (
            f"- {op.id} | {op.type.value} | acc={op.bank_account_id} | "
            f"{op.amount.as_str()} | {op.date.isoformat()}"
        )
        tail = f" | cat={op.category_id} | {op.description or ''}"
        print(base + tail)


def ensure_demo_data(c: Container):
    if list(c.accounts.list()):
        return
    print("Инициализация демо-данных...")
    acc = CreateAccountCommand(
        c.accounts,
        "Основной счет",
        Money.of("1000")).execute()
    food = CreateCategoryCommand(
        c.categories,
        CategoryType.EXPENSE,
        "Кафе").execute()
    salary = CreateCategoryCommand(
        c.categories,
        CategoryType.INCOME,
        "Зарплата").execute()
    AddOperationCommand(
        c.operations,
        OperationType.EXPENSE,
        acc.id,
        Money.of("250.50"),
        date.today().isoformat(),
        "обед",
        food.id).execute()
    AddOperationCommand(
        c.operations,
        OperationType.INCOME,
        acc.id,
        Money.of("1500.00"),
        date.today().isoformat(),
        "оклад",
        salary.id).execute()


def do_export(c: Container):
    fmt = pick([("json", "JSON"), ("yaml", "YAML"),
               ("csv", "CSV")], "Экспорт — формат")
    target = prompt("Путь назначения: ")
    snap = DataSnapshot(
        c.accounts.list(),
        c.categories.list(),
        c.operations.list_all())
    out = c.export.export_all(snap, fmt=fmt, target=target)
    print("Экспортировано:")
    for p in out:
        print(" -", p)


def do_import(c: Container):
    fmt = pick([("json", "JSON"), ("yaml", "YAML"),
               ("csv", "CSV")], "Импорт — формат")
    path = prompt("Путь к файлу: ")
    if fmt == "json":
        c.import_json.import_file(path)
    elif fmt == "yaml":
        c.import_yaml.import_file(path)
    else:
        c.import_csv.import_file(path)
    print("Импорт завершен.")


def do_analytics(c: Container):
    print("\n=== Аналитика ===")
    d1 = prompt("Дата от (YYYY-MM-DD): ")
    d2 = prompt("Дата до (YYYY-MM-DD): ")
    from datetime import datetime as _dt
    date_from = _dt.fromisoformat(d1).date()
    date_to = _dt.fromisoformat(d2).date()
    diff = c.analytics.difference_by_period(
        c.operations.list_all(), date_from, date_to)
    print(f"Сальдо за период: {diff.as_str()}")

    groups = c.analytics.grouped_by_category(c.operations.list_all())
    print("По категориям (sign=доход/расход):")
    id2name = {cat.id: cat.name for cat in c.categories.list()}
    for cid, money in groups.items():
        print(f" - {id2name.get(cid, cid)}: {money.as_str()}")


def main():
    print("FinTrack — учет финансов (OOП + паттерны).")
    c = Container(db_path=":memory:")
    ensure_demo_data(c)

    stats = StatsCollector()

    menu = [
        ("acc_list", "Показать счета"),
        ("acc_create", "Создать счет"),
        ("acc_update", "Переименовать счет"),
        ("acc_delete", "Удалить счет"),
        ("cat_list", "Показать категории"),
        ("cat_create", "Создать категорию"),
        ("cat_update", "Изменить категорию"),
        ("cat_delete", "Удалить категорию"),
        ("op_list", "Показать операции"),
        ("op_add", "Добавить операцию"),
        ("op_delete", "Удалить операцию"),
        ("op_recalc", "Пересчитать баланс счета"),
        ("analytics", "Аналитика"),
        ("export", "Экспорт"),
        ("import", "Импорт"),
        ("stats", "Статистика времени сценариев"),
        ("exit", "Выйти"),
    ]

    while True:
        code = pick(menu, "Главное меню")
        try:
            if code == "acc_list":
                show_accounts(c)
            elif code == "acc_create":
                name = prompt("Название счета: ")
                bal = Money.of(prompt("Начальный баланс: "))
                cmd = TimedCommandDecorator(
                    "CreateAccount",
                    CreateAccountCommand(c.accounts, name, bal),
                    stats,
                )
                acc = cmd.execute()
                print("Создан:", acc)
            elif code == "acc_update":
                show_accounts(c)
                acc_id = prompt("ID счета: ")
                new_name = prompt("Новое имя: ")
                cmd = TimedCommandDecorator(
                    "UpdateAccount",
                    UpdateAccountCommand(c.accounts, acc_id, new_name),
                    stats,
                )
                print("Готово:", cmd.execute())
            elif code == "acc_delete":
                show_accounts(c)
                acc_id = prompt("ID счета: ")
                TimedCommandDecorator(
                    "DeleteAccount", DeleteAccountCommand(
                        c.accounts, acc_id), stats).execute()
                print("Удалено.")
            elif code == "cat_list":
                show_categories(c)
            elif code == "cat_create":
                t = pick([("INCOME", "Доход"), ("EXPENSE", "Расход")],
                         "Тип категории")
                name = prompt("Название: ")
                cmd = TimedCommandDecorator(
                    "CreateCategory",
                    CreateCategoryCommand(c.categories, CategoryType(t), name),
                    stats,
                )
                print("Создано:", cmd.execute())

            elif code == "cat_update":
                show_categories(c)
                cid = prompt("ID категории: ")
                new_name = prompt(
                    "Новое название (пусто — без изменения): ") or None
                new_type = None
                if prompt("Менять тип? (y/N): ").lower() == "y":
                    t = pick(
                        [("INCOME", "Доход"), ("EXPENSE", "Расход")],
                        "Новый тип",
                    )
                    new_type = CategoryType(t)
                cmd = TimedCommandDecorator(
                    "UpdateCategory", UpdateCategoryCommand(
                        c.categories, cid, new_name, new_type), stats, )
                print("Готово:", cmd.execute())

            elif code == "cat_delete":
                show_categories(c)
                cid = prompt("ID категории: ")
                TimedCommandDecorator(
                    "DeleteCategory", DeleteCategoryCommand(
                        c.categories, cid), stats).execute()
                print("Удалено.")
            elif code == "op_list":
                show_operations(c)
            elif code == "op_add":
                show_accounts(c)
                acc_id = prompt("ID счета: ")
                t = pick([("INCOME", "Доход"), ("EXPENSE", "Расход")],
                         "Тип операции")
                cats = list(c.categories.list_by_type(CategoryType(t)))
                if not cats:
                    continue
                print("Категории подходящего типа:")
                for cat in cats:
                    print(f" - {cat.id} | {cat.type.value} | {cat.name}")
                cat_id = prompt("ID категории: ")
                amount = Money.of(prompt("Сумма: "))
                d = prompt("Дата (YYYY-MM-DD): ")
                desc = prompt("Описание (опционально): ") or None
                cmd = TimedCommandDecorator(
                    "AddOperation",
                    AddOperationCommand(
                        c.operations,
                        OperationType(t),
                        acc_id,
                        amount,
                        d,
                        desc,
                        cat_id),
                    stats,
                )
                print("Добавлено:", cmd.execute())
            elif code == "op_delete":
                show_operations(c)
                op_id = prompt("ID операции: ")
                TimedCommandDecorator(
                    "DeleteOperation", DeleteOperationCommand(
                        c.operations, op_id), stats).execute()
                print("Удалено.")
            elif code == "op_recalc":
                show_accounts(c)
                acc_id = prompt("ID счета: ")
                cmd = TimedCommandDecorator(
                    "RecalcBalance", RecalculateAccountBalanceCommand(
                        c.accounts, c.operations, acc_id), stats, )
                print("Пересчитано:", cmd.execute())
            elif code == "analytics":
                do_analytics(c)
            elif code == "export":
                do_export(c)
            elif code == "import":
                do_import(c)
            elif code == "stats":
                print("Среднее время выполнения сценариев:")
                for name, avg in stats.summary().items():
                    print(f" - {name}: {avg:.4f}s")
            elif code == "exit":
                print("До встречи!")
                break
        except Exception as e:
            print("Ошибка:", e)


if __name__ == "__main__":
    main()
