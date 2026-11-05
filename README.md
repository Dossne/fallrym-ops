# fallrym-ops

Служебный репозиторий Fallrym: отсюда демо уходит на itch, анонсы — в Дискорд, комментарии с itch собираются в файл.
Код игры живёт в другом репозитории; сюда кладётся только готовая сборка демо.

| Что | Как срабатывает | Workflow |
|---|---|---|
| Демо на itch.io | коммит в `demo/` (там `index.html` и `VERSION`) или ручной запуск | `.github/workflows/itch-push.yml` → `butler push demo dossne/fallrym:html5` |
| Пост в Дискорд от «Клавдия» | новый файл в `announce/*.md` | `.github/workflows/discord-post.yml` |
| Комментарии с itch | каждый день в 06:17 UTC или ручной запуск | `.github/workflows/itch-comments.yml` → `comments/itch.json`, `comments/new.md` |

Секреты (Settings → Secrets and variables → Actions), их видит только GitHub:
- `BUTLER_API_KEY` — ключ itch (itch.io → Settings → API keys).
- `DISCORD_WEBHOOK` — вебхук канала #announcements.

Правила:
- В `demo/` коммитим только с отмашки автора: это мажорная версия (`ОО.ДД`), она сразу уходит игрокам.
- Анонс — один файл на пост, имя `ГГГГ-ММ-ДД-тема.md`, текст автор одобрил заранее. Дискорд режет сообщения длиннее 2000 символов — скрипт делит по абзацам.
