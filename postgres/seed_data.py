"""
Генерация синтетических данных для 10 нефтегазовых таблиц.
Подключается к БД text_to_sql.
Запуск: python postgres/seed_data.py
"""
import os
import random
from datetime import date, timedelta
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

DB_URL = os.getenv("DATABASE_URL")

random.seed(42)

# ── справочники ────────────────────────────────────────────────────────────────

FIELD_NAMES = [
    "Самотлорское", "Ромашкинское", "Приобское", "Лянторское", "Фёдоровское",
    "Мамонтовское", "Салымское", "Правдинское", "Усть-Балыкское", "Нижневартовское",
    "Варьёганское", "Тевлинско-Русскинское", "Тарасовское", "Холмогорское",
    "Уренгойское", "Ямбургское", "Медвежье", "Бованенковское", "Заполярное",
    "Харасавейское", "Ново-Уренгойское", "Ен-Яхинское", "Находкинское",
    "Русановское", "Ленинградское", "Оренбургское", "Астраханское", "Карачаганакское",
    "Туймазинское", "Шкаповское", "Арланское", "Ново-Хазинское", "Серафимовское",
    "Красноярское", "Верхнечонское", "Юрубчено-Тохомское", "Куюмбинское",
    "Сузунское", "Тагульское", "Лодочное",
]
REGIONS = [
    "Ханты-Мансийский АО", "Ямало-Ненецкий АО", "Тюменская область",
    "Республика Татарстан", "Республика Башкортостан", "Оренбургская область",
    "Красноярский край", "Иркутская область", "Ненецкий АО", "Томская область",
]
OPERATORS = [
    "Роснефть", "ЛУКОЙЛ", "Газпром нефть", "Сургутнефтегаз", "Татнефть",
    "Башнефть", "Новатэк", "Газпром", "Славнефть", "РуссНефть",
]
FIELD_TYPES = ["нефтяное", "газовое", "нефтегазовое", "газоконденсатное"]
FIELD_STATUSES = ["разведка", "разработка", "консервация", "выработан"]

FORMATION_PREFIXES = ["АВ", "БВ", "ЮВ", "АС", "БС", "ЮС", "ПК", "Тр", "Д"]
FLUID_TYPES = ["нефть", "газ", "конденсат", "вода"]

WELL_TYPES = ["добывающая", "нагнетательная", "разведочная", "наблюдательная", "ликвидированная"]
WELL_STATUSES = ["в работе", "в простое", "в ремонте", "ликвидирована", "в консервации"]
WELL_TYPE_WEIGHTS = [55, 20, 10, 5, 10]

CATEGORIES = ["А", "В1", "В2", "С1", "С2"]
APPROVED_BY = [
    "ГКЗ Роснедра", "ТКЗ ХМАО", "ТКЗ ЯНАО", "ЦКР Роснедра",
    "Государственная комиссия по запасам",
]

REPAIR_TYPES_DATA = [
    ("КРС-01", "Смена насосного оборудования", "КРС"),
    ("КРС-02", "Ремонт колонны обсадных труб", "КРС"),
    ("КРС-03", "Ликвидация аварии с НКТ", "КРС"),
    ("КРС-04", "Перевод на другой пласт", "КРС"),
    ("КРС-05", "Зарезка бокового ствола", "КРС"),
    ("КРС-06", "Ремонт цементного кольца", "КРС"),
    ("КРС-07", "Ликвидация скважины", "КРС"),
    ("КРС-08", "Восстановление скважины после аварии", "КРС"),
    ("ПРС-01", "Смена глубинного насоса", "ПРС"),
    ("ПРС-02", "Ревизия подземного оборудования", "ПРС"),
    ("ПРС-03", "Промывка забоя скважины", "ПРС"),
    ("ПРС-04", "Замена НКТ", "ПРС"),
    ("ПРС-05", "Смена штангового насоса", "ПРС"),
    ("ПРС-06", "Ревизия пакера", "ПРС"),
    ("ГРП-01", "Многостадийный гидроразрыв пласта", "ГРП"),
    ("ГРП-02", "Одностадийный гидроразрыв пласта", "ГРП"),
    ("ГРП-03", "Повторный гидроразрыв пласта", "ГРП"),
    ("ОПЗ-01", "Кислотная обработка призабойной зоны", "ОПЗ"),
    ("ОПЗ-02", "Термохимическая обработка", "ОПЗ"),
    ("ОПЗ-03", "Соляно-кислотная обработка", "ОПЗ"),
    ("ОПЗ-04", "Депарафинизация скважины", "ОПЗ"),
    ("ОПЗ-05", "Глино-кислотная обработка", "ОПЗ"),
    ("ПР-01", "Исследование скважины КВД/КВУ", "прочее"),
    ("ПР-02", "Геофизические исследования в скважине", "прочее"),
    ("ПР-03", "Перфорация продуктивного пласта", "прочее"),
]
CONTRACTORS = [
    "СервисНефть", "БурСервис", "ТехноДрилл", "РемСкважина", "НефтеСервис",
    "ПодземСервис", "ГидроФрак", "АльфаДрилл", "ОмегаСервис", "СибБурение",
]
REPAIR_RESULTS = ["успешно", "частично", "безуспешно", "в процессе"]
REPAIR_RESULT_WEIGHTS = [70, 15, 10, 5]

EQUIPMENT_TYPES = ["ЭЦН", "ШГН", "Газлифт", "ЭВН", "УЭЦН", "ПЦН"]
MANUFACTURERS = [
    "Новомет", "Борец", "ЭлКамНасос", "Лифтнефть", "Алнас",
    "Weatherford", "Baker Hughes", "Halliburton", "Schlumberger",
]

SEVERITY = ["авария", "инцидент", "отказ", "замечание"]
SEVERITY_WEIGHTS = [5, 15, 40, 40]
INCIDENT_CAUSES = [
    "Износ оборудования", "Коррозия труб", "Отложение парафина",
    "Механическое повреждение", "Нарушение технологического режима",
    "Гидратообразование", "Разгерметизация пакера", "Обрыв штанговой колонны",
    "Отказ электродвигателя", "Засорение фильтра",
]
INCIDENT_DESCRIPTIONS = [
    "Отказ глубинного насоса, остановка скважины",
    "Разгерметизация НКТ на глубине {d} м",
    "Обрыв штанговой колонны, ликвидация аварии",
    "Прорыв воды из нагнетательного пласта",
    "Парафиновые отложения, снижение дебита на {p}%",
    "Отказ частотного преобразователя ЭЦН",
    "Коррозионное разрушение обсадной колонны",
    "Выброс пластового флюида при глушении скважины",
    "Обводнение продукции до {w}%",
    "Нарушение герметичности цементного кольца",
]

GTM_TYPES = [
    "Гидроразрыв пласта (ГРП)",
    "Оптимизация режима работы насоса",
    "Перевод скважины на другой горизонт",
    "Зарезка бокового ствола (ЗБС)",
    "Кислотная обработка (КО)",
    "Интенсификация добычи (ИД)",
    "Водоизоляционные работы (ВИР)",
    "Ввод скважины из простоя",
    "Форсированный отбор жидкости",
    "Нестационарное заводнение",
]
GTM_STATUSES = ["план", "выполнено", "отменено", "перенесено"]
GTM_STATUS_WEIGHTS = [15, 65, 10, 10]


# ── утилиты ────────────────────────────────────────────────────────────────────

def rdate(start_year=2000, end_year=2024) -> date:
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))


def first_of_month(start_year=2018, end_year=2024) -> date:
    d = rdate(start_year, end_year)
    return d.replace(day=1)


def wchoice(population, weights):
    return random.choices(population, weights=weights, k=1)[0]


# ── генераторы ─────────────────────────────────────────────────────────────────

def gen_fields(n=1000):
    rows = []
    names_pool = FIELD_NAMES * (n // len(FIELD_NAMES) + 1)
    for i in range(n):
        name = f"{names_pool[i]} {random.randint(1, 99)}"
        rows.append((
            name,
            random.choice(REGIONS),
            f"ЛУ-{random.randint(100, 999)}",
            random.randint(1950, 2020),
            random.choice(FIELD_TYPES),
            wchoice(FIELD_STATUSES, [5, 70, 15, 10]),
            random.choice(OPERATORS),
        ))
    return rows


def gen_formations(n=1000, field_ids=None):
    rows = []
    for _ in range(n):
        prefix = random.choice(FORMATION_PREFIXES)
        suffix = random.randint(1, 12)
        depth_top = round(random.uniform(800, 3500), 2)
        rows.append((
            random.choice(field_ids),
            f"{prefix}{suffix}",
            depth_top,
            round(depth_top + random.uniform(10, 80), 2),
            round(random.uniform(10, 35), 2),
            round(random.uniform(1, 500), 3),
            wchoice(FLUID_TYPES, [50, 30, 10, 10]),
        ))
    return rows


def gen_wells(n=1000, field_ids=None, formation_ids=None):
    rows = []
    for i in range(n):
        spud = rdate(1980, 2022)
        completion = spud + timedelta(days=random.randint(30, 180))
        wtype = wchoice(WELL_TYPES, WELL_TYPE_WEIGHTS)
        rows.append((
            str(random.randint(1, 9999)),
            random.choice(field_ids),
            random.choice(formation_ids),
            wtype,
            wchoice(WELL_STATUSES, [55, 15, 10, 10, 10]),
            spud,
            completion,
            round(random.uniform(800, 4000), 2),
            round(random.uniform(56, 72), 7),
            round(random.uniform(60, 90), 7),
        ))
    return rows


def gen_production(n=1000, well_ids=None):
    rows = []
    used = set()
    attempts = 0
    while len(rows) < n and attempts < n * 10:
        attempts += 1
        well_id = random.choice(well_ids)
        period = first_of_month()
        if (well_id, period) in used:
            continue
        used.add((well_id, period))
        work_days = random.randint(15, 30)
        rows.append((
            well_id,
            period,
            round(random.uniform(0, 500), 3),
            round(random.uniform(0, 50000), 3),
            round(random.uniform(0, 300), 3),
            work_days,
            30 - work_days,
        ))
    return rows


def gen_gas_reserves(n=1000, field_ids=None, formation_ids=None):
    rows = []
    for _ in range(n):
        rows.append((
            random.choice(field_ids),
            random.choice(formation_ids),
            rdate(2000, 2024),
            random.choice(CATEGORIES),
            round(random.uniform(0.01, 500), 4),
            round(random.uniform(0, 5000), 3),
            random.choice(APPROVED_BY),
        ))
    return rows


def gen_repair_types():
    return [(r[0], r[1], r[2]) for r in REPAIR_TYPES_DATA]


def gen_well_repairs(n=1000, well_ids=None, repair_type_ids=None):
    rows = []
    for _ in range(n):
        start = rdate(2010, 2024)
        end = start + timedelta(days=random.randint(3, 60)) if random.random() > 0.1 else None
        rows.append((
            random.choice(well_ids),
            random.choice(repair_type_ids),
            start,
            end,
            random.choice(CONTRACTORS),
            round(random.uniform(500_000, 50_000_000), 2),
            wchoice(REPAIR_RESULTS, REPAIR_RESULT_WEIGHTS),
            None,
        ))
    return rows


def gen_well_equipment(n=1000, well_ids=None):
    rows = []
    for _ in range(n):
        installed = rdate(2005, 2023)
        removed = installed + timedelta(days=random.randint(90, 1000)) if random.random() > 0.4 else None
        etype = random.choice(EQUIPMENT_TYPES)
        rows.append((
            random.choice(well_ids),
            etype,
            f"{etype}-{random.randint(100, 999)}-{random.randint(50, 250)}",
            random.choice(MANUFACTURERS),
            installed,
            removed,
            round(random.uniform(500, 3500), 2),
            "демонтировано" if removed else wchoice(["в работе", "отказ"], [85, 15]),
        ))
    return rows


def gen_incidents(n=1000, well_ids=None):
    rows = []
    for _ in range(n):
        severity = wchoice(SEVERITY, SEVERITY_WEIGHTS)
        resolved = random.random() > 0.15
        incident_date = rdate(2010, 2024)
        desc_template = random.choice(INCIDENT_DESCRIPTIONS)
        description = desc_template.format(
            d=random.randint(500, 3000),
            p=random.randint(10, 60),
            w=random.randint(50, 99),
        )
        rows.append((
            random.choice(well_ids),
            incident_date,
            severity,
            description,
            random.choice(INCIDENT_CAUSES),
            round(random.uniform(1, 720), 2),
            round(random.uniform(0, 50), 3),
            resolved,
            incident_date + timedelta(days=random.randint(1, 30)) if resolved else None,
        ))
    return rows


def gen_gtm(n=1000, well_ids=None):
    rows = []
    for _ in range(n):
        planned = rdate(2020, 2025)
        status = wchoice(GTM_STATUSES, GTM_STATUS_WEIGHTS)
        actual = planned + timedelta(days=random.randint(-10, 30)) if status == "выполнено" else None
        rows.append((
            random.choice(well_ids),
            random.choice(GTM_TYPES),
            planned,
            actual,
            round(random.uniform(0.5, 50), 3),
            round(random.uniform(100, 100000), 3),
            round(random.uniform(1_000_000, 100_000_000), 2),
            status,
        ))
    return rows


# ── вставка ────────────────────────────────────────────────────────────────────

def insert(cur, table, columns, rows):
    sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES %s"
    execute_values(cur, sql, rows)
    print(f"  ✓ {table}: {len(rows)} строк")


def main():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    print("Вставка данных...")

    # 1. fields
    insert(cur, "fields",
           ["name", "region", "license_area", "discovered_year", "field_type", "status", "operator"],
           gen_fields(1000))
    conn.commit()
    cur.execute("SELECT id FROM fields")
    field_ids = [r[0] for r in cur.fetchall()]

    # 2. formations
    insert(cur, "formations",
           ["field_id", "name", "depth_top_m", "depth_bottom_m", "porosity_pct", "permeability_md", "fluid_type"],
           gen_formations(1000, field_ids))
    conn.commit()
    cur.execute("SELECT id FROM formations")
    formation_ids = [r[0] for r in cur.fetchall()]

    # 3. wells
    insert(cur, "wells",
           ["well_number", "field_id", "formation_id", "well_type", "status",
            "spud_date", "completion_date", "depth_m", "lat", "lon"],
           gen_wells(1000, field_ids, formation_ids))
    conn.commit()
    cur.execute("SELECT id FROM wells")
    well_ids = [r[0] for r in cur.fetchall()]

    # 4. production
    insert(cur, "production",
           ["well_id", "period_date", "oil_tonnes", "gas_m3", "water_m3", "work_days", "downtime_days"],
           gen_production(1000, well_ids))
    conn.commit()

    # 5. gas_reserves
    insert(cur, "gas_reserves",
           ["field_id", "formation_id", "reserve_date", "category", "gas_bcm", "condensate_kt", "approved_by"],
           gen_gas_reserves(1000, field_ids, formation_ids))
    conn.commit()

    # 6. repair_types (справочник — только уникальные)
    rt_rows = gen_repair_types()
    insert(cur, "repair_types", ["code", "name", "category"], rt_rows)
    conn.commit()
    cur.execute("SELECT id FROM repair_types")
    repair_type_ids = [r[0] for r in cur.fetchall()]

    # 7. well_repairs
    insert(cur, "well_repairs",
           ["well_id", "repair_type_id", "start_date", "end_date", "contractor", "cost_rub", "result", "notes"],
           gen_well_repairs(1000, well_ids, repair_type_ids))
    conn.commit()

    # 8. well_equipment
    insert(cur, "well_equipment",
           ["well_id", "equipment_type", "model", "manufacturer",
            "installed_date", "removed_date", "depth_m", "status"],
           gen_well_equipment(1000, well_ids))
    conn.commit()

    # 9. incidents
    insert(cur, "incidents",
           ["well_id", "incident_date", "severity", "description", "cause",
            "downtime_hours", "loss_oil_tonnes", "resolved", "resolved_date"],
           gen_incidents(1000, well_ids))
    conn.commit()

    # 10. gtm
    insert(cur, "gtm",
           ["well_id", "gtm_type", "planned_date", "actual_date",
            "oil_effect_t", "gas_effect_m3", "cost_rub", "status"],
           gen_gtm(1000, well_ids))
    conn.commit()

    cur.close()
    conn.close()
    print("\nГотово. Все таблицы наполнены.")


if __name__ == "__main__":
    main()
