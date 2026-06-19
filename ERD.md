# ERD — Планировщик студента (расширенная схема)

## Таблицы и поля

---

### 1. `subjects` — Предметы

| Поле       | Тип     | Описание                          |
|------------|---------|-----------------------------------|
| id         | INTEGER | PRIMARY KEY AUTOINCREMENT         |
| name       | TEXT    | Название предмета (UNIQUE)        |
| teacher    | TEXT    | ФИО преподавателя                 |
| room       | TEXT    | Аудитория                         |
| color      | TEXT    | HEX-цвет для отображения в UI     |
| created_at | TEXT    | Дата добавления предмета          |

---

### 2. `tags` — Теги

| Поле  | Тип     | Описание                     |
|-------|---------|------------------------------|
| id    | INTEGER | PRIMARY KEY AUTOINCREMENT    |
| name  | TEXT    | Название тега (UNIQUE)       |
| color | TEXT    | HEX-цвет тега                |

---

### 3. `tasks` — Задачи

| Поле            | Тип     | Описание                                      |
|-----------------|---------|-----------------------------------------------|
| id              | INTEGER | PRIMARY KEY AUTOINCREMENT                     |
| title           | TEXT    | Название задачи (NOT NULL)                    |
| description     | TEXT    | Описание задачи                               |
| subject_id      | INTEGER | FK → subjects(id) ON DELETE SET NULL          |
| task_type       | TEXT    | homework / lab / exam / other                 |
| deadline        | TEXT    | Дедлайн: YYYY-MM-DD HH:MM                    |
| priority        | INTEGER | 1=высокий, 2=средний, 3=низкий               |
| status          | TEXT    | pending / done                                |
| grade           | TEXT    | Оценка (текст, после выполнения)              |
| grade_value     | REAL    | Числовое значение оценки (для аналитики)      |
| feedback        | TEXT    | Отзыв преподавателя                           |
| estimated_hours | REAL    | Ожидаемое время выполнения (часы)             |
| actual_hours    | REAL    | Фактически потраченное время (часы)           |
| notify_enabled  | INTEGER | Уведомление вкл/выкл (0 или 1)               |
| notify_minutes  | INTEGER | За сколько минут до дедлайна уведомить        |
| notification_id | TEXT    | ID активного системного уведомления           |
| created_at      | TEXT    | Дата создания                                 |
| updated_at      | TEXT    | Дата последнего изменения                     |

---

### 4. `task_tags` — Связь задача ↔ тег (M:N)

| Поле    | Тип     | Описание                              |
|---------|---------|---------------------------------------|
| task_id | INTEGER | FK → tasks(id) ON DELETE CASCADE      |
| tag_id  | INTEGER | FK → tags(id)  ON DELETE CASCADE      |
| PRIMARY KEY | — | (task_id, tag_id) составной ключ      |

---

### 5. `attachments` — Вложения к задачам

| Поле        | Тип     | Описание                            |
|-------------|---------|-------------------------------------|
| id          | INTEGER | PRIMARY KEY AUTOINCREMENT           |
| task_id     | INTEGER | FK → tasks(id) ON DELETE CASCADE    |
| filename    | TEXT    | Имя файла                           |
| filepath    | TEXT    | Путь к файлу на диске               |
| uploaded_at | TEXT    | Дата загрузки                       |

---

### 6. `audit_log` — Журнал изменений

| Поле       | Тип     | Описание                              |
|------------|---------|---------------------------------------|
| id         | INTEGER | PRIMARY KEY AUTOINCREMENT             |
| task_id    | INTEGER | FK → tasks(id) ON DELETE SET NULL     |
| action     | TEXT    | CREATE / UPDATE / DELETE              |
| old_value  | TEXT    | Старое значение (JSON или строка)     |
| new_value  | TEXT    | Новое значение (JSON или строка)      |
| changed_at | TEXT    | Дата и время изменения                |

---

## Связи между таблицами

```
subjects (1) ────────────── (N) tasks
                                   │
                tasks (N) ────── (N) tags
                      [через task_tags]
                                   │
                tasks (1) ────── (N) attachments
                                   │
                tasks (1) ────── (N) audit_log
```

## Диаграмма (текстовая)

```
┌──────────────────────┐        ┌──────────────────────────────────────────┐
│       subjects       │        │                   tasks                  │
├──────────────────────┤        ├──────────────────────────────────────────┤
│ PK  id    INTEGER    │◄───┐   │ PK  id              INTEGER              │
│     name  TEXT UNIQ  │    └── │ FK  subject_id      INTEGER              │
│     teacher  TEXT    │        │     title           TEXT  NOT NULL        │
│     room     TEXT    │        │     description     TEXT                 │
│     color    TEXT    │        │     task_type       TEXT  DEFAULT homework│
│     created_at TEXT  │        │     deadline        TEXT                 │
└──────────────────────┘        │     priority        INTEGER DEFAULT 2    │
                                │     status          TEXT  DEFAULT pending │
                                │     grade           TEXT                 │
┌──────────────────────┐        │     grade_value     REAL                 │
│        tags          │        │     feedback        TEXT                 │
├──────────────────────┤        │     estimated_hours REAL                 │
│ PK  id    INTEGER    │        │     actual_hours    REAL                 │
│     name  TEXT UNIQ  │        │     notify_enabled  INTEGER DEFAULT 0    │
│     color TEXT       │        │     notify_minutes  INTEGER DEFAULT 30   │
└──────────┬───────────┘        │     notification_id TEXT                 │
           │                    │     created_at      TEXT                 │
           │  ┌─────────────┐   │     updated_at      TEXT                 │
           └──┤  task_tags  ├───┘          │
              ├─────────────┤              │
              │ FK task_id  │         ┌────┴─────────────────────┐
              │ FK tag_id   │         │       attachments        │
              │ PK (оба)    │         ├─────────────────────────-┤
              └─────────────┘         │ PK  id          INTEGER  │
                                      │ FK  task_id     INTEGER  │
                                      │     filename    TEXT     │
              ┌───────────────────┐   │     filepath    TEXT     │
              │     audit_log     │   │     uploaded_at TEXT     │
              ├───────────────────┤   └──────────────────────────┘
              │ PK  id  INTEGER   │
              │ FK  task_id       │
              │     action  TEXT  │
              │     old_value TEXT│
              │     new_value TEXT│
              │     changed_at    │
              └───────────────────┘
```

## Индексы

| Индекс              | Таблица | Колонка    | Цель                             |
|---------------------|---------|------------|----------------------------------|
| idx_tasks_status    | tasks   | status     | Быстрый фильтр по статусу        |
| idx_tasks_deadline  | tasks   | deadline   | Сортировка/фильтр по дедлайну    |
| idx_tasks_subject   | tasks   | subject_id | JOIN с subjects                  |
| idx_audit_task      | audit_log | task_id  | История изменений задачи         |

## Ключевые решения

- `subject_id` вместо текстового поля `subject` — нормализация, исключает опечатки
- `grade_value REAL` рядом с `grade TEXT` — текст для отображения, число для аналитики (средний балл)
- `task_tags` (M:N) — одна задача может иметь несколько тегов, один тег — несколько задач
- `attachments` — каждая задача может иметь несколько прикреплённых файлов
- `audit_log` — полная история всех изменений для прозрачности
- `estimated_hours / actual_hours` — позволяет анализировать точность планирования
- `ON DELETE CASCADE` в task_tags и attachments — при удалении задачи всё связанное удаляется автоматически
- `ON DELETE SET NULL` в tasks.subject_id — при удалении предмета задачи не теряются
