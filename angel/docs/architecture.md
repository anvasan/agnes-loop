# Angel — AI-маркетолог softzor.com.ua

## Архитектура

```
┌─────────────────────────────────────┐
│           👤 Василий (anvasan)      │
│         Команды / Ревью / Расписание│
└────────────────┬────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      🤖 Agent: Angel                                 │
│                                                                      │
│  Core Skill → загружает Brain Base из Softzor_AI_Brain_Base44/      │
│                                                                      │
│  Skills:                                                               │
│  ├── software-card    → создание карточек ПО в WP                    │
│  ├── blog-writer      → SEO статьи для блога                          │
│  ├── social-poster    → посты для соцсетей                            │
│  ├── gsc-analytics    → Google Search Console API                   │
│  ├── ga-analytics     → Google Analytics 4 API                       │
│  └── daily-routine    → утренний/вечерний круги                      │
│                                                                      │
│  Scripts:                                                              │
│  ├── wp_helper.py          → WP REST API интерфейс                   │
│  ├── gsc_analytics.py      → GSC API клиент                          │
│  └── ga_analytics.py       → GA4 API клиент                          │
└──┬───────────────┬───────────────┬───────────────┬──────────────────┘
   │               │               │               │
   ▼               ▼               ▼               ▼
┌──────┐ ┌──────────────┐ ┌──────────┐ ┌──────────────────┐
│ WordPress  │ │ Гугл Серч │ Google   │ │ Brain Base       │
│ REST API   │ │ Console   │ Analytcs │ │ Obsidian Vault   │
│             │ │ API       │ API      │ │                  │
│ wp/v2/     │ │           │          │ │ Softzor_AI_      │
│ software   │ │ GSC data  │ GA4 data │ │ Brain_Base44/    │
│             │ │           │          │ │ Categories,      │
│ softmir/v1 │ │           │          │ │ Tracker, Rules   │
│ enrich     │ │           │          │                    │
└────────────┘ └────────────┘ └──────────┘ └──────────────────┘
```

## Источники данных

### Brain Base (статические знания)
`G:/Мой диск/Softzor_AI_Brain_Base44/`

### WordPress API (динамические данные)
- Категории, атрибуты, черновики, метрики

### Google Search Console (метрики поиска)
- Позиции, клики, показы по запросам

### Google Analytics 4 (метрики сайта)
- Трафик, поведение пользователей, источники

## Обновление Brain Base

После каждого обновления категорий сайта (добавление новых категорий, изменение атрибутов):

1. Получить актуальные данные через API
2. Обновить `Categories_Reference.md` в Obsidian
3. Обновить трекер программ
4. Зафиксировать изменения в `04_Decisions_Log.md`
