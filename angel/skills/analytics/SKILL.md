---
name: analytics
description: "Настройка и аудит аналитики для softzor.com.ua. GA4 tracking, UTM parameters, tag manager, conversion tracking."
tags: [analytics, ga4, tracking, conversion]
---

# 📊 Analytics (для SoftZor)

## Core Principles
1. **Track for decisions, not data** — каждое событие должно влиять на решение
2. **Start with questions** — сначала вопрос, потом что трекать
3. **Consistent naming** — lowercase_underscore
4. **Data quality > quantity** — чистые данные важнее объёма

## Event Naming Convention
Формат: `object_action`
Примеры: `signup_completed`, `article_read`, `software_card_view`

## Essential Events для каталога ПО
| Event | Properties | Trigger |
|-------|-----------|---------|
| software_card_view | software_id, category | Просмотр карточки |
| software_search | query, category | Поиск по каталогу |
| blog_post_view | post_id, category | Просмотр статьи |
| social_link_click | platform, source | Клик из соцсетей |
| cta_clicked | button_text, location | CTA клик |
| form_submitted | form_type | Форма отправлена |

## UTM Parameters Standard
| Parameter | Purpose | Example |
|-----------|---------|---------|
| utm_source | traffic source | telegram, facebook |
| utm_medium | marketing medium | social, referral |
| utm_campaign | campaign name | july_2026 |
| utm_content | differentiate | hero_cta |
| utm_term | paid keywords | running+shoes |

### Rules
- lowercase everything
- Use underscores consistently
- Document all UTMs
- Never include PII

## Debug & Validation
| Check | Pass/Fail |
|-------|-----------|
| Events fire on correct triggers | |
| Property values populated | |
| No duplicate events | |
| Works across browsers | |
| No PII leaking | |
| GA4 DebugView shows live events | |
