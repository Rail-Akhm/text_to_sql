-- =============================================================
-- Text-to-SQL: DDL для нефтегазовой отрасли
-- =============================================================

-- 1. Месторождения
CREATE TABLE fields (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,                  -- Название месторождения
    region          VARCHAR(100),                           -- Регион / субъект РФ
    license_area    VARCHAR(100),                           -- Лицензионный участок
    discovered_year INT,                                    -- Год открытия
    field_type      VARCHAR(50) CHECK (field_type IN ('нефтяное', 'газовое', 'нефтегазовое', 'газоконденсатное')),
    status          VARCHAR(50) CHECK (status IN ('разведка', 'разработка', 'консервация', 'выработан')),
    operator        VARCHAR(200),                           -- Компания-оператор
    created_at      TIMESTAMP DEFAULT NOW()
);

-- 2. Пласты (геологические горизонты)
CREATE TABLE formations (
    id              SERIAL PRIMARY KEY,
    field_id        INT REFERENCES fields(id),
    name            VARCHAR(100) NOT NULL,                  -- Название пласта (АВ1, БВ8 и т.д.)
    depth_top_m     NUMERIC(8,2),                           -- Глубина кровли, м
    depth_bottom_m  NUMERIC(8,2),                           -- Глубина подошвы, м
    porosity_pct    NUMERIC(5,2),                           -- Пористость, %
    permeability_md NUMERIC(10,3),                          -- Проницаемость, мД
    fluid_type      VARCHAR(50) CHECK (fluid_type IN ('нефть', 'газ', 'конденсат', 'вода'))
);

-- 3. Скважины
CREATE TABLE wells (
    id              SERIAL PRIMARY KEY,
    well_number     VARCHAR(50) NOT NULL,                   -- Номер скважины
    field_id        INT REFERENCES fields(id),
    formation_id    INT REFERENCES formations(id),
    well_type       VARCHAR(50) CHECK (well_type IN ('добывающая', 'нагнетательная', 'разведочная', 'наблюдательная', 'ликвидированная')),
    status          VARCHAR(50) CHECK (status IN ('в работе', 'в простое', 'в ремонте', 'ликвидирована', 'в консервации')),
    spud_date       DATE,                                   -- Дата начала бурения
    completion_date DATE,                                   -- Дата окончания бурения
    depth_m         NUMERIC(8,2),                           -- Глубина скважины, м
    lat             NUMERIC(10,7),                          -- Широта
    lon             NUMERIC(10,7),                          -- Долгота
    created_at      TIMESTAMP DEFAULT NOW()
);

-- 4. Добыча (ежемесячные показатели)
CREATE TABLE production (
    id              SERIAL PRIMARY KEY,
    well_id         INT REFERENCES wells(id),
    period_date     DATE NOT NULL,                          -- Месяц отчёта (первое число месяца)
    oil_tonnes      NUMERIC(12,3),                          -- Добыча нефти, тонн
    gas_m3          NUMERIC(15,3),                          -- Добыча газа, м³
    water_m3        NUMERIC(12,3),                          -- Добыча воды, м³
    work_days       INT,                                    -- Дней работы в месяце
    downtime_days   INT,                                    -- Дней простоя
    UNIQUE (well_id, period_date)
);

-- 5. Запасы газа
CREATE TABLE gas_reserves (
    id              SERIAL PRIMARY KEY,
    field_id        INT REFERENCES fields(id),
    formation_id    INT REFERENCES formations(id),
    reserve_date    DATE NOT NULL,                          -- Дата оценки запасов
    category        VARCHAR(10) CHECK (category IN ('А', 'В1', 'В2', 'С1', 'С2')),  -- Категория запасов
    gas_bcm         NUMERIC(12,4),                          -- Запасы газа, млрд м³
    condensate_kt   NUMERIC(12,3),                          -- Запасы конденсата, тыс. тонн
    approved_by     VARCHAR(200)                            -- Утверждающий орган
);

-- 6. Типы ремонтов скважин
CREATE TABLE repair_types (
    id              SERIAL PRIMARY KEY,
    code            VARCHAR(20) UNIQUE NOT NULL,            -- Код КРС/ПРС
    name            VARCHAR(200) NOT NULL,                  -- Название вида ремонта
    category        VARCHAR(50) CHECK (category IN ('КРС', 'ПРС', 'ГРП', 'ОПЗ', 'прочее'))
                                                            -- КРС-капитальный, ПРС-подземный, ГРП-гидроразрыв
);

-- 7. Ремонты скважин
CREATE TABLE well_repairs (
    id              SERIAL PRIMARY KEY,
    well_id         INT REFERENCES wells(id),
    repair_type_id  INT REFERENCES repair_types(id),
    start_date      DATE NOT NULL,                          -- Дата начала ремонта
    end_date        DATE,                                   -- Дата окончания ремонта
    contractor      VARCHAR(200),                           -- Подрядчик
    cost_rub        NUMERIC(15,2),                          -- Стоимость ремонта, руб.
    result          VARCHAR(50) CHECK (result IN ('успешно', 'частично', 'безуспешно', 'в процессе')),
    notes           TEXT                                    -- Примечания
);

-- 8. Оборудование скважин
CREATE TABLE well_equipment (
    id              SERIAL PRIMARY KEY,
    well_id         INT REFERENCES wells(id),
    equipment_type  VARCHAR(100),                           -- Тип оборудования (ЭЦН, ШГН, газлифт и т.д.)
    model           VARCHAR(200),                           -- Модель / марка
    manufacturer    VARCHAR(200),                           -- Производитель
    installed_date  DATE,                                   -- Дата установки
    removed_date    DATE,                                   -- Дата демонтажа
    depth_m         NUMERIC(8,2),                           -- Глубина спуска, м
    status          VARCHAR(50) CHECK (status IN ('в работе', 'демонтировано', 'отказ'))
);

-- 9. Инциденты и аварии
CREATE TABLE incidents (
    id              SERIAL PRIMARY KEY,
    well_id         INT REFERENCES wells(id),
    incident_date   DATE NOT NULL,                          -- Дата инцидента
    severity        VARCHAR(20) CHECK (severity IN ('авария', 'инцидент', 'отказ', 'замечание')),
    description     TEXT,                                   -- Описание
    cause           VARCHAR(200),                           -- Причина
    downtime_hours  NUMERIC(8,2),                           -- Простой, часов
    loss_oil_tonnes NUMERIC(10,3),                          -- Потери нефти, тонн
    resolved        BOOLEAN DEFAULT FALSE,
    resolved_date   DATE
);

-- 10. Геолого-технические мероприятия (ГТМ)
CREATE TABLE gtm (
    id              SERIAL PRIMARY KEY,
    well_id         INT REFERENCES wells(id),
    gtm_type        VARCHAR(100),                           -- Вид ГТМ
    planned_date    DATE,                                   -- Плановая дата
    actual_date     DATE,                                   -- Фактическая дата
    oil_effect_t    NUMERIC(10,3),                          -- Эффект по нефти, тонн/сут
    gas_effect_m3   NUMERIC(12,3),                          -- Эффект по газу, м³/сут
    cost_rub        NUMERIC(15,2),                          -- Затраты, руб.
    status          VARCHAR(50) CHECK (status IN ('план', 'выполнено', 'отменено', 'перенесено'))
);
