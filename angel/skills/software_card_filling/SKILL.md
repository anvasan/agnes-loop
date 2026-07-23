---
name: software-card
description: "Создание карточек ПО в WordPress. Исследование продукта через enrichment API, подбор категорий/атрибутов из кэша, формирование 6 HTML-блоков full_description."
tags: [wordpress, content, card, filling]
---

# 📦 Наполнение карточки ПО (SoftZor)

## Когда активировать
- «создай карточку https://example.com»
- «обнови существующую карточку»
- Упоминание «карточка ПО», «softzor», «enrich»

## Алгоритм работы (пошаговый)

### ШАГ 1. Чтение справочников (БЕЗ ТЕРМИНАЛА)

Доступны локально:
- `D:/laragon/www/Marketolog/.agents/cache/categories.json` — категории
- `D:/laragon/www/Marketolog/.agents/cache/attributes.json` — атрибуты

В `categories.json` для каждой категории есть массив `key_functions` — это ЕДИНСТВЕННЫЙ допустимый источник для чекбоксов.

### ШАГ 2. Исследование продукта (Enrichment API)

Создать скрипт и запустить:
```python
import urllib.request, json, base64

wp_url = "http://softzor.test"
auth_b64 = base64.b64encode(b"admin:fLbVEJGFwjyARuUAsXKen8hu").decode("utf-8")
url_to_analyze = "ССЫЛКА_НА_САЙТ_ПРОДУКТА"

req = urllib.request.Request(
    f"{wp_url}/wp-json/softmir/v1/extract-facts",
    data=json.dumps({"url": url_to_analyze}).encode("utf-8"),
    method="POST"
)
req.add_header("Content-Type", "application/json")
req.add_header("Authorization", f"Basic {auth_b64}")

response = urllib.request.urlopen(req)
result = json.loads(response.read().decode("utf-8"))
print(json.dumps(result, ensure_ascii=False, indent=2))
```

Данные из JSON (`features`, `advantages`, `disadvantages`, `pricing_list`) использовать СТРОГО их.
Если API ошибается → резервный вариант с `search_web`.

### ШАГ 3. Подбор категорий и атрибутов

#### 3.1 Основная категория (`primary_category_id`)
Одна категория, лучше всего описывающая продукт. Фильтр по русскоязычным названиям.

#### 3.2 Дополнительные категории (`software_categories`)
Массив ID всех релевантных категорий.

#### 3.3 Ключевые функции (`category_key_functions`)
**КРИТИЧНО:** Строки ДОЛЖНЫ ТОЧНО совпадать со значениями из `key_functions` основной категории из кэша. ЗАПРЕЩЕНО выдумывать.

#### 3.4 Обязательные атрибуты (ID → обязательные поля):
| ID | Поле |
|----|------|
| 425 | Платформы |
| 426 | Языки интерфейса |
| 427 | Модель оплаты |
| 428 | Размер бизнеса |
| 430 | Тип установки |
| 1302 | Отрасли бизнеса |

### ШАГ 4. Формирование контента (Payload)

#### 4.1 Полный HTML (`full_description`) — строго 6 блоков

**БЛОК 1 — ЛИД:**
```html
<p>🟢 <b>Релевантность: [85-99]% (Одобрено редактором)</b><br>
<b>Почему SoftZor рекомендует:</b> [3-4 предложения. Суть + боль].</p>
```

**БЛОК 2 — ЭКСПЕРТНЫЙ ВЕРДИКТ:**
```html
<h3>⚖️ Экспертный вердикт SoftZor</h3>
<p><b>Кому брать:</b> [1 предложение].</p>
<p><b>Кому обходить стороной:</b> [1 предложение].</p>
<p><b>⚡ Порог входа:</b> [Низкий/Средний/Высокий]</p>
<blockquote><b>💡 Совет практика:</b> [лайфхак].</blockquote>
```

**БЛОК 3 — ГЛАВНЫЕ ФУНКЦИИ:**
```html
<h3>⚙️ Главные функции</h3>
<table class="table table-striped">
<tr><td><b>Название</b></td><td>Описание.</td></tr>
<!-- мин. 3 строки -->
</table>
```

**БЛОК 4 — КОНКУРЕНТЫ:**
```html
<h3>🔄 Аналоги</h3>
<ul><li><b>Название:</b> Отличие.</li></ul> <!-- 2-4 штуки -->
```

**БЛОК 5 — ОТЗЫВЫ:**
```html
<h3>🗣️ Отзывы пользователей</h3>
<blockquote><b>[Источник]:</b> "[Цитата]"</blockquote>
```

**БЛОК 6 — ЦЕНЫ:**
```html
<h3>💰 Цены и тарифы</h3>
<p><b>Модель оплаты:</b> ...<br><b>Стоимость:</b> ...<br><b>⚠️ Скрытые платежи:</b> ...</p>
```

### ШАГ 5. Единый скрипт (1 вызов терминала)

Сгенерировать ОДИН python-скрипт:
```python
import urllib.request, json, base64

wp_url = "http://softzor.test"
auth_b64 = base64.b64encode(b"admin:fLbVEJGFwjyARuUAsXKen8hu").decode("utf-8")

# 1. Создать черновик
req1 = urllib.request.Request(
    f"{wp_url}/wp-json/wp/v2/software",
    data=json.dumps({"title": "...", "status": "draft"}).encode("utf-8"),
    method="POST"
)
req1.add_header("Content-Type", "application/json")
req1.add_header("Authorization", f"Basic {auth_b64}")
post_id = json.loads(urllib.request.urlopen(req1).read().decode("utf-8"))["id"]

# 2. Payload с id
payload = {
    "ID": post_id,
    "title": "...",
    "short_description": "...",
    "full_description": "...",  # 6 HTML блоков
    "price_summary": "От $X/мес",
    "advantages": ["...", "..."],
    "disadvantages": ["...", "...", "..."],  # минимум 3!
    "best_for": ["...", "..."],
    "bad_for": ["...", "..."],
    "scenarios": [{"title": "...", "desc": "..."}],  # ровно 3 штуки
    "features": ["...", "..."],
    "integrations": [...],
    "primary_category_id": 54,
    "software_categories": [54, 59],
    "category_key_functions": ["..."],
    "attributes": [{"id": 425, "value": ["Веб-версия"]}, ...],
    "origin": "US",
    "verdict": "...",
    "pricing_list": [{"plan": "Free", "price": "0", "currency": "USD"}],
    "external_reviews": [{"source": "Capterra", "rating": "4.5"}]
}

# 3. Обогащение
req2 = urllib.request.Request(
    f"{wp_url}/wp-json/softmir/v1/enrich-software",
    data=json.dumps(payload).encode("utf-8"),
    method="POST"
)
req2.add_header("Content-Type", "application/json")
req2.add_header("Authorization", f"Basic {auth_b64}")
print("Enriched:", json.loads(urllib.request.urlopen(req2).read()))
```

## ⛔ Критические запреты
1. **НИКОГДА** не выдумывать `category_key_functions` — только из кэша
2. **НИКОГДА** пропускать блоки в `full_description` — все 6 обязательны
3. **НИКОГДА** не дублировать `short_description` и блок «Почему SoftZor рекомендует»
4. **МИНИМУМ** 3 пункта в `disadvantages`
5. **ЗАПРЕЩЕНЫ** слова: инновационный, комплексное решение, уникальный

## 🔗 После создания
1. Обновить трекер программ → `...Proposed_Programs_Tracker.md`
2. Проверить категорию: если 5+ опубликованных → предложить статью
3. Предложить пост для соцсетей
4. Записать в журнал работы
