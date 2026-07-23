#!/usr/bin/env python3
"""
GSC Analytics для softzor.com.ua
Подключается к Google Search Console API, извлекает данные по позициям, CTR, кликам.
Анализирует метрики по категориям ПО и предлагает действия.

Использование:
  python gsc_analytics.py --query "crm" --days 28
  python gsc_analytics.py --all-categories --days 90
  python gsc_analytics.py --recommendations --days 30

Требуется: Google Cloud Service Account JSON с доступом к GSC.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


def get_gsc_client(creds_path: str):
    """Инициализирует Google Search Console API client."""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        creds = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=['https://www.googleapis.com/auth/webmasters.readonly']
        )
        return build('searchconsole', 'v1', credentials=creds)
    except ImportError:
        print("ОШИБКА: Установите google-api-python-client: pip install google-api-python-client google-auth")
        sys.exit(1)


def get_site_url(api):
    """Получает site URL из GSC API."""
    sites = api.sites().list().execute()
    for site in sites.get('siteEntry', []):
        # softzor.com.ua
        if 'softzor' in site.get('siteUrl', ''):
            return site['siteUrl']
    return None


def query_gsc(api, site_url, query=None, days=28):
    """Запрашивает данные из GSC API."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    body = {
        'startDate': start_date,
        'endDate': end_date,
        'dimension': ['query', 'page'],
    }

    if query:
        body['dimension'] = ['query']
        body['searchType'] = 'web'
        # Note: GSC API v1 doesn't support query filter directly in search API
        # We'll filter results after getting data

    request = api.searchanalytics().query(
        siteUrl=site_url,
        body=body
    )

    return request.execute()


def get_page_metrics(api, site_url, category_slug, days=28):
    """Получает метрики для страницы/категории."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    body = {
        'startDate': start_date,
        'endDate': end_date,
        'dimension': ['query', 'page'],
        'dimensionFilterGroup': {
            'filters': [{
                'dimension': 'page',
                'expression': f'{site_url.rstrip("/")}/software/{category_slug}',
                'operator': 'contains'
            }]
        }
    }

    request = api.searchanalytics().query(
        siteUrl=site_url,
        body=body
    )

    return request.execute()


def analyze_metrics(data, site_url):
    """Анализирует данные из GSC, возвращает insights."""
    rows = data.get('rows', [])

    total_clicks = sum(r.get('clicks', 0) for r in rows)
    total_impressions = sum(r.get('impressions', 0) for r in rows)
    avg_ctr = sum(r.get('ctr', 0) * r.get('impressions', 0) for r in rows) / total_clicks if total_clicks > 0 else 0
    avg_position = sum(r.get('positions', 0) * r.get('impressions', 0) for r in rows) / total_impressions if total_impressions > 0 else 0

    insights = {
        'period': f'{data.get("startDate", "N/A")} — {data.get("endDate", "N/A")}',
        'total_clicks': total_clicks,
        'total_impressions': total_impressions,
        'avg_ctr': round(avg_ctr, 3),
        'avg_position': round(avg_position, 1),
        'top_queries': [],
        'lost_opportunities': [],
        'action_items': []
    }

    # Top queries by clicks
    sorted_by_clicks = sorted(rows, key=lambda r: r.get('clicks', 0), reverse=True)[:10]
    for row in sorted_by_clicks:
        insights['top_queries'].append({
            'query': row.get('query', ''),
            'clicks': row.get('clicks', 0),
            'impressions': row.get('impressions', 0),
            'ctr': round(row.get('ctr', 0), 3),
            'position': round(row.get('positions', 0), 1)
        })

    # Lost opportunities: high impressions but low position
    for row in rows:
        if row.get('impressions', 0) > 50 and row.get('positions', 0) > 10:
            insights['lost_opportunities'].append({
                'query': row.get('query', ''),
                'impressions': row.get('impressions', 0),
                'position': round(row.get('positions', 0), 1),
                'potential': f"Позиция {row.get('positions', 0)} — есть потенциал роста в ТОП-10"
            })

    # Action items
    if avg_ctr < 0.03:
        insights['action_items'].append("⚠️ Низкий CTR (<3%) — пересмотреть meta-title и meta-description страниц ПО")
    if avg_position > 15:
        insights['action_items'].append("📉 Средняя позиция >15 — приоритизировать SEO-оптимизацию карточек ТОП-программ")
    if len(insights['lost_opportunities']) > 5:
        insights['action_items'].append(f"💡 Найдено {len(insights['lost_opportunities'])} запросов с большим количеством показов на низких позициях — создать статьи под эти запросы")

    return insights


def generate_recommendations(insights, categories_data=None):
    """Генерирует рекомендации по контенту на основе аналитики."""
    recs = []

    if 'action_items' in insights:
        for item in insights['action_items']:
            recs.append({'type': 'priority', 'action': item})

    # По lost opportunities → предлагаемые темы статей
    for opp in insights.get('lost_opportunities', [])[:5]:
        query = opp['query']
        recs.append({
            'type': 'blog_post',
            'title': f"Статья: Обзор решений по запросу «{query}»",
            'reason': f"{opp['impressions']} показов на позиции {opp['position']} — есть трафик",
            'priority': 'high' if opp['impressions'] > 100 else 'medium'
        })

    return recs


def main():
    parser = argparse.ArgumentParser(description='GSC Analytics для softzor.com.ua')
    parser.add_argument('--creds', required=True, help='Путь к Google Service Account JSON')
    parser.add_argument('--query', help='Фильтр по запросу')
    parser.add_argument('--days', type=int, default=28, help='Диапазон дней (по умолчанию 28)')
    parser.add_argument('--output', help='Файл для сохранения результатов JSON')
    args = parser.parse_args()

    api = get_gsc_client(args.creds)
    site_url = get_site_url(api)

    if not site_url:
        print("ОШИБКА: Сайт softzor.com.ua не найден в GSC")
        sys.exit(1)

    print(f"📊 Запрос данных из GSC ({site_url}, последние {args.days} дней)...")

    data = query_gsc(api, site_url, query=args.query, days=args.days)
    insights = analyze_metrics(data, site_url)

    print(f"\n{'='*60}")
    print(f"GSC Analytics — softzor.com.ua")
    print(f"Период: {insights['period']}")
    print(f"{'='*60}")
    print(f"📈 Клики:       {insights['total_clicks']}")
    print(f"👁️ Показы:      {insights['total_impressions']}")
    print(f"🎯 CTR:          {insights['avg_ctr']:.1%}")
    print(f"📍 Позиция:      {insights['avg_position']}")

    print(f"\nТоп запросов:")
    for q in insights['top_queries'][:5]:
        print(f"  {q['query']:40s} CTR:{q['ctr']:.1%}  Pos:{q['position']:.1f}  Imp:{q['impressions']}")

    recommendations = generate_recommendations(insights)
    if recommendations:
        print(f"\n💡 Рекомендации:")
        for r in recommendations:
            print(f"  [{r['type']}] {r.get('reason', r.get('action', ''))}")

    # Output
    result = {**insights, 'recommendations': recommendations}

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n📄 Сохранено в {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == '__main__':
    main()
