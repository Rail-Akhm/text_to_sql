-- =============================================================
-- Схема EDM: единый каталог данных
-- =============================================================

CREATE SCHEMA IF NOT EXISTS edm;

CREATE TABLE edm.data_catalog (
    id            SERIAL PRIMARY KEY,
    schema_name   VARCHAR(100) NOT NULL DEFAULT 'public',
    table_name    VARCHAR(100) NOT NULL,
    column_name   VARCHAR(100) NOT NULL,
    description   TEXT,
    embedding     FLOAT8[],
    UNIQUE (schema_name, table_name, column_name)
);

-- =============================================================
-- Наполнение каталога
-- =============================================================

INSERT INTO edm.data_catalog (schema_name, table_name, column_name, description) VALUES

-- fields
('public', 'fields', 'id',             'Уникальный идентификатор месторождения'),
('public', 'fields', 'name',           'Название месторождения'),
('public', 'fields', 'region',         'Регион или субъект РФ, в котором расположено месторождение'),
('public', 'fields', 'license_area',   'Название лицензионного участка'),
('public', 'fields', 'discovered_year','Год открытия месторождения'),
('public', 'fields', 'field_type',     'Тип месторождения: нефтяное, газовое, нефтегазовое, газоконденсатное'),
('public', 'fields', 'status',         'Текущий статус месторождения: разведка, разработка, консервация, выработан'),
('public', 'fields', 'operator',       'Компания-оператор месторождения'),
('public', 'fields', 'created_at',     'Дата и время создания записи'),

-- formations
('public', 'formations', 'id',              'Уникальный идентификатор пласта'),
('public', 'formations', 'field_id',        'Ссылка на месторождение (fields.id)'),
('public', 'formations', 'name',            'Название геологического пласта или горизонта (например АВ1, БВ8)'),
('public', 'formations', 'depth_top_m',     'Глубина кровли пласта в метрах'),
('public', 'formations', 'depth_bottom_m',  'Глубина подошвы пласта в метрах'),
('public', 'formations', 'porosity_pct',    'Пористость пласта в процентах'),
('public', 'formations', 'permeability_md', 'Проницаемость пласта в миллидарси (мД)'),
('public', 'formations', 'fluid_type',      'Тип флюида в пласте: нефть, газ, конденсат, вода'),

-- wells
('public', 'wells', 'id',              'Уникальный идентификатор скважины'),
('public', 'wells', 'well_number',     'Номер скважины'),
('public', 'wells', 'field_id',        'Ссылка на месторождение (fields.id)'),
('public', 'wells', 'formation_id',    'Ссылка на эксплуатируемый пласт (formations.id)'),
('public', 'wells', 'well_type',       'Тип скважины: добывающая, нагнетательная, разведочная, наблюдательная, ликвидированная'),
('public', 'wells', 'status',          'Текущий статус скважины: в работе, в простое, в ремонте, ликвидирована, в консервации'),
('public', 'wells', 'spud_date',       'Дата начала бурения скважины'),
('public', 'wells', 'completion_date', 'Дата окончания бурения скважины'),
('public', 'wells', 'depth_m',         'Глубина скважины в метрах'),
('public', 'wells', 'lat',             'Географическая широта устья скважины'),
('public', 'wells', 'lon',             'Географическая долгота устья скважины'),
('public', 'wells', 'created_at',      'Дата и время создания записи'),

-- production
('public', 'production', 'id',            'Уникальный идентификатор записи добычи'),
('public', 'production', 'well_id',       'Ссылка на скважину (wells.id)'),
('public', 'production', 'period_date',   'Отчётный месяц (первое число месяца)'),
('public', 'production', 'oil_tonnes',    'Добыча нефти за месяц в тоннах'),
('public', 'production', 'gas_m3',        'Добыча газа за месяц в кубических метрах'),
('public', 'production', 'water_m3',      'Добыча воды за месяц в кубических метрах'),
('public', 'production', 'work_days',     'Количество рабочих дней скважины в месяце'),
('public', 'production', 'downtime_days', 'Количество дней простоя скважины в месяце'),

-- gas_reserves
('public', 'gas_reserves', 'id',            'Уникальный идентификатор записи запасов'),
('public', 'gas_reserves', 'field_id',      'Ссылка на месторождение (fields.id)'),
('public', 'gas_reserves', 'formation_id',  'Ссылка на пласт (formations.id)'),
('public', 'gas_reserves', 'reserve_date',  'Дата оценки или утверждения запасов'),
('public', 'gas_reserves', 'category',      'Категория запасов по российской классификации: А, В1, В2, С1, С2'),
('public', 'gas_reserves', 'gas_bcm',       'Запасы газа в миллиардах кубических метров'),
('public', 'gas_reserves', 'condensate_kt', 'Запасы газового конденсата в тысячах тонн'),
('public', 'gas_reserves', 'approved_by',   'Орган, утвердивший запасы'),

-- repair_types
('public', 'repair_types', 'id',       'Уникальный идентификатор типа ремонта'),
('public', 'repair_types', 'code',     'Код вида ремонта'),
('public', 'repair_types', 'name',     'Полное название вида ремонта скважины'),
('public', 'repair_types', 'category', 'Категория ремонта: КРС (капитальный), ПРС (подземный), ГРП (гидроразрыв пласта), ОПЗ (обработка призабойной зоны)'),

-- well_repairs
('public', 'well_repairs', 'id',             'Уникальный идентификатор ремонта'),
('public', 'well_repairs', 'well_id',        'Ссылка на скважину (wells.id)'),
('public', 'well_repairs', 'repair_type_id', 'Ссылка на тип ремонта (repair_types.id)'),
('public', 'well_repairs', 'start_date',     'Дата начала ремонта'),
('public', 'well_repairs', 'end_date',       'Дата окончания ремонта'),
('public', 'well_repairs', 'contractor',     'Подрядная организация, выполнявшая ремонт'),
('public', 'well_repairs', 'cost_rub',       'Стоимость ремонта в рублях'),
('public', 'well_repairs', 'result',         'Результат ремонта: успешно, частично, безуспешно, в процессе'),
('public', 'well_repairs', 'notes',          'Дополнительные примечания по ремонту'),

-- well_equipment
('public', 'well_equipment', 'id',             'Уникальный идентификатор записи оборудования'),
('public', 'well_equipment', 'well_id',        'Ссылка на скважину (wells.id)'),
('public', 'well_equipment', 'equipment_type', 'Тип глубинного оборудования: ЭЦН, ШГН, газлифт и др.'),
('public', 'well_equipment', 'model',          'Модель или марка оборудования'),
('public', 'well_equipment', 'manufacturer',   'Производитель оборудования'),
('public', 'well_equipment', 'installed_date', 'Дата установки оборудования в скважину'),
('public', 'well_equipment', 'removed_date',   'Дата демонтажа оборудования из скважины'),
('public', 'well_equipment', 'depth_m',        'Глубина спуска оборудования в метрах'),
('public', 'well_equipment', 'status',         'Статус оборудования: в работе, демонтировано, отказ'),

-- incidents
('public', 'incidents', 'id',               'Уникальный идентификатор инцидента'),
('public', 'incidents', 'well_id',          'Ссылка на скважину (wells.id)'),
('public', 'incidents', 'incident_date',    'Дата возникновения инцидента или аварии'),
('public', 'incidents', 'severity',         'Степень серьёзности: авария, инцидент, отказ, замечание'),
('public', 'incidents', 'description',      'Подробное описание инцидента'),
('public', 'incidents', 'cause',            'Причина возникновения инцидента'),
('public', 'incidents', 'downtime_hours',   'Время простоя скважины из-за инцидента в часах'),
('public', 'incidents', 'loss_oil_tonnes',  'Потери нефти в результате инцидента в тоннах'),
('public', 'incidents', 'resolved',         'Признак устранения инцидента (true/false)'),
('public', 'incidents', 'resolved_date',    'Дата устранения инцидента'),

-- gtm
('public', 'gtm', 'id',            'Уникальный идентификатор геолого-технического мероприятия'),
('public', 'gtm', 'well_id',       'Ссылка на скважину (wells.id)'),
('public', 'gtm', 'gtm_type',      'Вид геолого-технического мероприятия'),
('public', 'gtm', 'planned_date',  'Плановая дата проведения ГТМ'),
('public', 'gtm', 'actual_date',   'Фактическая дата проведения ГТМ'),
('public', 'gtm', 'oil_effect_t',  'Ожидаемый или фактический эффект по нефти в тоннах в сутки'),
('public', 'gtm', 'gas_effect_m3', 'Ожидаемый или фактический эффект по газу в кубических метрах в сутки'),
('public', 'gtm', 'cost_rub',      'Затраты на проведение ГТМ в рублях'),
('public', 'gtm', 'status',        'Статус ГТМ: план, выполнено, отменено, перенесено');
