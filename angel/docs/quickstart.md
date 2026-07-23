---
team: DEV
created: 2026-07-23
branch: task/angel-marketolog
tz-file: angel-marketolog.md
---

# Angel — AI-маркетолог softzor.com.ua

## Quick Start

1. Загрузить skill `angel-core` для основного контекста
2. Для создания карточки ПО: `load skill software-card` → `[карточка] Название`
3. Для статьи блога: `load skill blog-writer` → `[контент] Тема`
4. Для поста в соцсети: `load skill social-poster` → `[пост] Тема`
5. Для аналитики GSC: `python scripts/gsc_analytics.py --creds path/to/service_account.json --query "keyword"`
6. Для аналитики GA4: `python scripts/ga_analytics.py --creds path/to/service_account.json --property-id 123456789`

## Требуемые данные для запуска

| Данные | Где взять | Когда нужно |
|--------|-----------|-------------|
| WP Application Password | WordPress Admin → Users → Application Passwords | Всегда |
| GSC API ключи | Google Cloud Console → Service Account | Фаза 2 (есть позже) |
| GA4 API ключи | Google Cloud Console + Google Analytics | Фаза 2 (есть позже) |
