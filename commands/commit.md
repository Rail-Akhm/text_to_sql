# Commit Convention

## Format

```
<type>(<scope>): <description>
```

## Types

- `feat` — новая функциональность
- `fix` — исправление бага
- `refactor` — рефакторинг без изменения поведения
- `docs` — документация
- `chore` — настройка, зависимости, CI
- `test` — тесты
- `style` — форматирование, линтинг

## Scope (optional)

Модуль или компонент: `ui`, `db`, `embeddings`, `vector`, `schema`, `sql`, `config`

## Rules

- Сообщение на русском
- Описание с маленькой буквы, без точки в конце
- Максимум 72 символа в первой строке
- Если коммит ломает обратную совместимость — добавить `BREAKING CHANGE:` в тело

## Examples

```
feat(parser): добавлен сборщик сообщений telegram
fix(db): исправлен дубликат при повторной вставке
refactor(bot): классификация вынесена в отдельный модуль
chore: обновлены зависимости
docs: добавлена конвенция коммитов
```

## Git commands

```bash
git add -A && git commit -m "feat(scope): description" && git push
```
