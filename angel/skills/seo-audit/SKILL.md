---
name: seo-audit
description: "SEO аудит сайта: технический, on-page, AI SEO. Оптимизация для поисковых систем и AI-поисковиков. Используется для softzor.com.ua."
tags: [seo, audit, ai-seo, optimization]
---

# 🔍 SEO Audit & AI SEO

## Когда активировать
- Аудит SEO: «почему не ранжируюсь», «потеря позиций», «проверь SEO»
- AI SEO: «оптимизируй для AI Overviews», «LLM citations»
- Технический аудит: «speed check», «Core Web Vitals»

## Приоритеты аудита
1. **Crawlability & Indexation** — может ли Google найти?
2. **Technical Foundations** — скорость, HTTPS, Core Web Vitals
3. **On-Page Optimization** — мета, заголовки, ключевые слова
4. **Content Quality** — стоит ли ранжироваться?
5. **Authority & Links** — есть ли авторитет?

## Технический SEO

### Crawlability
- robots.txt: нет блокировок важных страниц
- XML Sitemap: существует, актуален, в Search Console
- Архитектура: важные страницы ≤ 3 кликов от главной

### Indexation
- `site:softzor.com.ua` проверка
- Нет noindex на важных страницах
- Canonical правильные, само-референсные
- Нет redirect chains / loops / soft 404

### Core Web Vitals
| Метрика | Цель |
|---------|------|
| LCP | < 2.5s |
| INP | < 200ms |
| CLS | < 0.1 |

### Mobile-Friendliness
- Responsive design
- Tap targets ≥ 48px
- Viewport configured
- Mobile-first indexing ready

## AI SEO — для SoftZor

AI системы извлекают отрывки, не целые страницы. Каждая важная_claim_ должна работать как standalone.

### Patternы для AI extraction
- **Definition blocks** — для «Что такое X?»
- **Comparison tables** — для «X vs Y»
- **Pros/cons blocks** — для оценки
- **FAQ blocks** — для естественных вопросов
- **Statistic blocks** — с цитируемыми источниками

### 9 методов оптимизации (Princeton GEO research)
| Метод | Boost | Как применить |
|-------|-------|---------------|
| Цитирование источников | +40% | Добавить ссылки на авторитетные |
| Статистика | +37% | Конкретные числа с источниками |
| Кавытки экспертов | +30% | Имя + должность |
| Авторитетный тон | +25% | Демонстрация экспертизы |
| Прозрачность | +20% | Упрощение сложных концепций |
| Термины | +18% | Domain-specific terminology |
| Уникальность | +15% | Словарное разнообразие |
| Читаемость | +15–30% | Readability и flow |
| Keyword stuffing | **-10%** | **Активно вредит!** |

### Best combo: Fluency + Statistics = max boost

### Structure rules
- Приводи прямой ответ в каждом разделе (не прячь!)
- Ключевые отрывки 40–60 слов (optimal для snippet extraction)
- H2/H3 заголовкиmatching queries
- Таблици > текст для сравнений
- Нумерованные списки > параграфы для процессов

### Schema markup для AI
| Тип контента | Schema | Зачем |
|-------------|--------|-------|
| Статьи | Article, BlogPosting | Автор, дата |
| HowTo | HowTo | Step extraction |
| FAQ | FAQPage | Direct Q&A |
| Products | Product | Цены, отзывы |
| Comparisons | ItemList | Structured data |

### Machine-readable files для AI Agents
Добавить к корню:
- `/pricing.md` — структурированные цены
- `/llms.txt` — контекст для AI
- `/okf/` — Open Knowledge Format bundle

## Monitoring
- AI Overview presence для топ-20 queries
- Brand citation rate
- Share of AI voice vs competitors
- Citation sentiment
