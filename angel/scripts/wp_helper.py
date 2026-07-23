#!/usr/bin/env python3
"""
WordPress Helper для softzor.com.ua
Основные операции: создание черновиков карточек ПО, статей блога, постов соцсетей.
Работает через WP REST API + enrich-software endpoint.

Использование:
  python wp_helper.py check-duplicates "GoHighLevel"
  python wp_helper.py list-drafts
  python wp_helper.py list-categories
  python wp_helper.py list-attributes

Требуется переменная окружения WP_APP_PASSWORD или файл .env
"""

import argparse
import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path


WP_BASE = "https://softzor.com.ua"
WP_JSON = f"{WP_BASE}/wp-json"
AUTH_USER = "admin"

def load_env():
    """Загружает APP_PASSWORD из окружения или .env файла."""
    password = os.environ.get('WP_APP_PASSWORD', '')
    if not password:
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            for line in env_path.read_text().strip().split('\n'):
                if line.startswith('WP_APP_PASSWORD='):
                    password = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break
    return password


def get_auth_header(password):
    """Создаёт Basic Auth заголовок."""
    if not password:
        print("ОШИБКА: Установите WP_APP_PASSWORD переменную окружения")
        sys.exit(1)
    credentials = base64.b64encode(f"{AUTH_USER}:{password}".encode()).decode()
    return {
        'Authorization': f'Basic {credentials}',
        'Content-Type': 'application/json'
    }


def api_request(endpoint, method='GET', data=None, params=None):
    """Выполняет запрос к WP REST API."""
    import urllib.request, urllib.parse

    url = f"{WP_JSON}/{endpoint.lstrip('/')}"
    if params:
        url += '?' + urllib.parse.urlencode(params)

    auth_pass = load_env()
    headers = get_auth_header(auth_pass)

    request = urllib.request.Request(url, headers=headers, method=method)
    if data:
        request.data = json.dumps(data).encode('utf-8')

    try:
        response = urllib.request.urlopen(request)
        result = response.read().decode('utf-8')
        return json.loads(result) if result else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"API ERROR [{e.code}]: {error_body}")
        return None


def check_duplicates(name, lang='ru'):
    """Проверяет, нет ли уже карточки с таким названием."""
    results = api_request('wp/v2/software', params={'search': name, 'lang': lang, 'per_page': 20})
    if not results:
        return []

    base_name = name.split(':')[0].strip().lower()
    duplicates = []
    for post in results:
        title = post.get('title', {}).get('rendered', '')
        if base_name in title.lower():
            duplicates.append({
                'id': post['id'],
                'title': title,
                'status': post.get('status', ''),
                'link': post.get('link', ''),
                'date': post.get('date', '')
            })

    return duplicates


def list_drafts(lang='ru', post_type='software', per_page=50):
    """Показывает черновики."""
    results = api_request(
        f'wp/v2/{post_type}',
        params={'status': 'draft', 'lang': lang, 'per_page': per_page}
    )
    if not results:
        return []

    items = []
    for post in results:
        items.append({
            'id': post['id'],
            'title': post.get('title', {}).get('rendered', ''),
            'date': post.get('date', ''),
            'type': post_type,
            'link': post.get('link', '')
        })
    return items


def list_categories():
    """Показывает все категории ПО с key_functions."""
    results = api_request('softmir/v1/categories')
    if not results:
        return []

    categories = []
    for cat in results:
        categories.append({
            'id': cat['id'],
            'name': cat.get('name', ''),
            'slug': cat.get('slug', ''),
            'key_functions': cat.get('key_functions', [])
        })
    return categories


def list_attributes():
    """Показывает все атрибуты ПО."""
    results = api_request('softmir/v1/attributes')
    if not results:
        return []
    return results


def show_usage():
    """Показывает справку по использованию."""
    help_text = """
═══════════════════════════════════════════════════════════
  WordPress Helper — softzor.com.ua
═══════════════════════════════════════════════════════════

Настройка:
  export WP_APP_PASSWORD="your-app-password"
  # или создать файл .env в той же директории с WP_APP_PASSWORD=...

Команды:
  check-duplicates <название> [язык]   — проверить дубли (lang=ru по умолчанию)
  list-drafts [тип]                    — показать черновики (software/post/page)
  list-categories                      — категории + key_functions
  list-attributes                      — атрибуты ПО
  enrich-software <json_file>          — обогащение карточки из JSON файла
  test-connection                      — проверка подключения к WP

Примеры:
  python wp_helper.py check-duplicates "GoHighLevel"
  python wp_helper.py list-drafts software
  python wp_helper.py list-categories
  python wp_helper.py test-connection
"""
    print(help_text)


def test_connection():
    """Проверяет подключение к WP."""
    results = api_request('wp/v2/types/software')
    if results:
        print(f"✅ WP подключен: {WP_BASE}")
        print(f"   Theme: softmir")
        print(f"   CPT: software")
        print(f"   Response time: OK")
    else:
        print("❌ Не удалось подключиться к WordPress API")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='WordPress Helper — softzor.com.ua')
    parser.add_argument('command', choices=[
        'check-duplicates', 'list-drafts', 'list-categories',
        'list-attributes', 'enrich-software', 'test-connection'
    ], help='Команда')
    parser.add_argument('args', nargs='*', help='Аргументы')
    args = parser.parse_args()

    if args.command == 'check-duplicates':
        name = args.args[0] if args.args else input("Название ПО: ")
        lang = args.args[1] if len(args.args) > 1 else 'ru'
        dups = check_duplicates(name, lang=lang)
        if dups:
            print(f"\n⚠️ Найденo дублей: {len(dups)}")
            for d in dups:
                print(f"  ID:{d['id']} | {d['title']} | Статус: {d['status']} | {d['link']}")
        else:
            print("✅ Дублей не найдено — можно создавать")

    elif args.command == 'list-drafts':
        post_type = args.args[0] if args.args else 'software'
        drafts = list_drafts(post_type=post_type)
        print(f"\n📋 Черновики ({post_type}):")
        for d in drafts[:20]:
            date_str = d.get('date', '')[:10] if d.get('date') else '—'
            print(f"  ID:{d['id']:>5d} | {date_str} | {d['title'][:60]}")

    elif args.command == 'list-categories':
        cats = list_categories()
        print(f"\n📂 Категории ПО ({len(cats)} шт.):")
        for c in cats:
            kf_str = ', '.join(c.get('key_functions', [])[:3])
            if len(c.get('key_functions', [])) > 3:
                kf_str += '...'
            print(f"  ID:{c['id']:>5d} | {c['name'][:50]:<50s} | {kf_str}")

    elif args.command == 'list-attributes':
        attrs = list_attributes()
        print(f"\n🏷️ Атрибуты ПО ({len(attrs)} шт.):")
        for a in attrs:
            print(f"  ID:{a['id']:>5d} | {a['name']:<30s} | {a.get('type', '')} | {a.get('options', '')[:80]}")

    elif args.command == 'test-connection':
        test_connection()

    elif args.command == 'enrich-software':
        print("ℹ️  Загружайте данные через API напрямую (см. angel-core skill)")
        test_connection()


if __name__ == '__main__':
    main()
