#!/usr/bin/env python3
"""
GA4 Analytics для softzor.com.ua
Подключается к Google Analytics 4 API, извлекает метрики органического трафика.
Анализирует популярные страницы, источники трафика, поведение пользователей.

Использование:
  python ga_analytics.py --creds service_account.json --property-id 123456789
  python ga_analytics.py --property-id 123456789 --metric "organic" --days 30
  python ga_analytics.py --property-id 123456789 --top-pages

Требуется: Google Cloud Service Account JSON с доступом к GA4.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


def get_ga_client(creds_path: str):
    """Инициализирует Google Analytics Data API v1 client."""
    try:
        from google.oauth2 import service_account
        from google.analytics.data_v1beta import BetaAnalyticsDataClient

        creds = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        return BetaAnalyticsDataClient(credentials=creds)
    except ImportError:
        print("ОШИБКА: Установите google-analytics-data: pip install google-analytics-data")
        sys.exit(1)


def get_organic_traffic(client, property_id, days=30):
    """Извлекает данные об органическом трафике за указанный период."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    response = client.run_report(
        property=f'properties/{property_id}',
        date_ranges=[
            (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')),
        ],
        metrics=[
            {'name': 'activeUsers'},
            {'name': 'screenPageViews'},
            {'name': 'averageSessionDuration'},
            {'name': 'sessionsPerUser'},
        ],
        dimensions=[
            {'name': 'country'},
            {'name': 'sessionDefaultChannelGroup'},
        ],
        dimension_filters={
            'dimension_name': 'sessionDefaultChannelGroup',
            'string_filter': {
                'match_type': 'EXACT',
                'value': 'Organic Search'
            }
        },
    )

    return response


def get_top_pages(client, property_id, days=30, limit=20):
    """Получает топ страниц по просмотрам."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    response = client.run_report(
        property=f'properties/{property_id}',
        date_ranges=[
            (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')),
        ],
        metrics=[{'name': 'screenPageViews'}],
        dimensions=[{'name': 'pagePath'}],
        order_bys=[{
            'metric': {'metric_name': 'screenPageViews'},
            'desc': True
        }],
        limit=limit,
    )

    return response


def get_content_categories(client, property_id, days=30):
    """Получает статистику по категориям ПО (software taxonomy)."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    response = client.run_report(
        property=f'properties/{property_id}',
        date_ranges=[
            (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')),
        ],
        dimensions=[{'name': 'customEvent:software_category'}],
        metrics=[
            {'name': 'screenPageViews'},
            {'name': 'activeUsers'},
            {'name': 'newUsers'},
        ],
        dimension_filters={
            'and_group': {
                'expressions': [
                    {
                        'dimension': {
                            'dimension_name': 'pagePath',
                            'exact': '/software/'
                        }
                    }
                ]
            }
        },
        limit=50,
    )

    return response


def analyze_traffic(data):
    """Анализирует данные GA4, возвращает insights."""
    rows = data.rows or []
    
    total_users = 0
    total_views = 0
    category_data = {}

    for row in rows:
        dimension_values = row.dimension_values
        metric_values = row.metric_values

        # Determine by dimension type
        if len(dimension_values) >= 2:
            country = dimension_values[0].value
            channel = dimension_values[1].value
        else:
            channel = 'Unknown'
            country = 'All'

        users = int(metric_values[0].value) if len(metric_values) > 0 else 0
        views = int(metric_values[1].value) if len(metric_values) > 1 else 0
        duration = float(metric_values[2].value) if len(metric_values) > 2 else 0

        total_users += users
        total_views += views
        category_data[country] = {
            'users': total_users,
            'views': total_views,
            'channel': channel
        }

    return {
        'total_users': total_users,
        'total_page_views': total_views,
        'avg_session_duration': round(duration / max(total_users, 1), 1) if total_users > 0 else 0,
        'categories': category_data
    }


def generate_recommendations(insights):
    """Генерирует рекомендации на основе аналитики GA4."""
    recs = []

    # Если Украина < 50% трафика — усилить UA-локализацию
    ua_traffic = insights.get('categories', {}).get('Ukraine', {})
    total = max(insights.get('total_users', 1), 1)
    ua_pct = (ua_traffic.get('users', 0) / total * 100) if 'Ukraine' in insights['categories'] else 60

    if ua_pct < 60:
        recs.append(f"⚠️ Трафик из Украины только {ua_pct:.0f}% — усилить UA-контент и локализацию")

    # Общие рекомендации
    if insights.get('total_users', 0) < 100:
        recs.append("📉 Низкий органический трафик — приоритизировать создание SEO-статей под пробелы категорий")

    recs.append("📊 Рекомендация: регулярно запускать этот скрипт и сравнивать тренды в Obsidian Brain/Журнал_Работы")

    return recs


def main():
    parser = argparse.ArgumentParser(description='GA4 Analytics для softzor.com.ua')
    parser.add_argument('--creds', required=True, help='Путь к Google Service Account JSON')
    parser.add_argument('--property-id', required=True, help='GA4 Property ID (пр. 123456789)')
    parser.add_argument('--days', type=int, default=30, help='Диапазон дней (по умолчанию 30)')
    parser.add_argument('--top-pages', action='store_true', help='Показать топ страниц')
    parser.add_argument('--output', help='Файл для сохранения результатов JSON')
    args = parser.parse_args()

    client = get_ga_client(args.creds)

    if args.top_pages:
        print(f"📄 Топ страниц за последние {args.days} дней...")
        response = get_top_pages(client, args.property_id, days=args.days, limit=20)

        pages = []
        for row in response.rows or []:
            path = row.dimension_values[0].value if row.dimension_values else 'Unknown'
            views = int(row.metric_values[0].value) if row.metric_values else 0
            pages.append({'path': path, 'views': views})

        print("\nТоп страниц:")
        for i, p in enumerate(pages[:10], 1):
            print(f"  {i:2d}. {p['views']:>5d}  {p['path']}")

        # Filter for software pages and blog posts
        software_pages = [p for p in pages if '/software/' in p['path']]
        blog_pages = [p for p in pages if '/blog/' in p['path']]

        print(f"\n📊 Страницы ПО: {len(software_pages)}")
        for p in software_pages[:5]:
            print(f"  {p['views']:>5d}  {p['path']}")
            
        print(f"\n📝 Статьи блога: {len(blog_pages)}")
        for p in blog_pages[:5]:
            print(f"  {p['views']:>5d}  {p['path']}")

    else:
        print(f"📊 Запрос данных из GA4 (property {args.property_id}, {args.days} дней)...")
        response = get_organic_traffic(client, args.property_id, days=args.days)
        insights = analyze_traffic(response)

        print(f"\n{'='*60}")
        print(f"GA4 Analytics — softzor.com.ua")
        print(f"{'='*60}")
        print(f"👥 Пользователи:     {insights['total_users']}")
        print(f"📄 Страницы:         {insights['total_page_views']}")
        print(f"⏱️ Avg сессия:       {insights['avg_session_duration']}с")

        recommendations = generate_recommendations(insights)
        print(f"\n💡 Рекомендации:")
        for r in recommendations:
            print(f"  {r}")

    result = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'property_id': args.property_id,
        'days': args.days,
        **insights
    }

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n📄 Сохранено в {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == '__main__':
    main()
