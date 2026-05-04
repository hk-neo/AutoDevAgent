#!/usr/bin/env python3
"""
티켓 타입별 필드 구조 비교 도구

여러 타입의 Jira 티켓 URL을 받아서 각 타입에 필요한 필드들을 비교 분석합니다.
"""

import json
import os
import sys
from collections import defaultdict
from typing import Dict, Any, List, Set

try:
    from jira import JIRA
except ImportError:
    print("Error: jira library not installed. Run: pip install jira")
    sys.exit(1)


class TypeComparator:
    def __init__(self, jira_url: str, email: str, api_token: str):
        self.jira = JIRA(server=jira_url, basic_auth=(email, api_token))

    def get_type_fields(self, ticket_url: str) -> Dict[str, Any]:
        """특정 티켓에서 해당 타입의 필드 구조 추출"""
        from analyze_ticket import JiraFieldAnalyzer
        analyzer = JiraFieldAnalyzer(self.jira.client_info, '', '')
        ticket_id = analyzer.parse_ticket_url(ticket_url)
        if not ticket_id:
            raise ValueError(f"Invalid URL: {ticket_url}")

        issue = self.jira.issue(ticket_id)
        issue_type = str(issue.fields.issuetype)

        field_definitions = analyzer.get_field_definitions(ticket_id)

        return {
            'ticket_id': ticket_id,
            'issue_type': issue_type,
            'fields': field_definitions,
            'url': ticket_url
        }

    def compare(self, ticket_urls: List[str]) -> Dict[str, Any]:
        """여러 티켓 타입 비교 분석"""
        type_data = {}

        for url in ticket_urls:
            print(f"Analyzing: {url}")
            data = self.get_type_fields(url)
            issue_type = data['issue_type']

            if issue_type not in type_data:
                type_data[issue_type] = {
                    'type': issue_type,
                    'tickets': [],
                    'fields': {},
                    'common_fields': set(),
                    'unique_fields': set()
                }

            type_data[issue_type]['tickets'].append(data['ticket_id'])

            # 필드 정보 수집
            for field_id, field_info in data['fields'].items():
                if field_id not in type_data[issue_type]['fields']:
                    type_data[issue_type]['fields'][field_id] = field_info

        # 타입 간 비교
        return self._compare_types(type_data)

    def _compare_types(self, type_data: Dict[str, Any]) -> Dict[str, Any]:
        """타입 간 필드 비교 분석"""
        types = list(type_data.keys())
        comparison = {
            'types': types,
            'type_details': {},
            'common_fields': set(type_data[types[0]]['fields'].keys()),
            'unique_by_type': {},
            'field_usage': defaultdict(set)
        }

        # 모든 타입의 필드 수집
        for issue_type, data in type_data.items():
            comparison['type_details'][issue_type] = {
                'field_count': len(data['fields']),
                'tickets': data['tickets']
            }
            comparison['common_fields'] &= set(data['fields'].keys())

            for field_id in data['fields'].keys():
                comparison['field_usage'][field_id].add(issue_type)

        # 고유 필드 식별
        for issue_type, data in type_data.items():
            other_types = set(types) - {issue_type}
            other_fields = set()
            for ot in other_types:
                other_fields.update(type_data[ot]['fields'].keys())

            unique = set(data['fields'].keys()) - other_fields
            comparison['unique_by_type'][issue_type] = list(unique)

        # 세트를 리스트로 변환
        comparison['common_fields'] = list(comparison['common_fields'])
        comparison['field_usage'] = {
            k: list(v) for k, v in comparison['field_usage'].items()
        }

        return comparison


def main():
    if len(sys.argv) < 3:
        print("Usage: python compare-types.py <ticket-url-1> <ticket-url-2> ...")
        print("Example:")
        print("  python compare-types.py \\")
        print("    https://domain.atlassian.net/browse/PROJ-123 \\")
        print("    https://domain.atlassian.net/browse/PROJ-456 \\")
        print("    https://domain.atlassian.net/browse/PROJ-789")
        sys.exit(1)

    ticket_urls = sys.argv[1:]
    jira_url = os.getenv('JIRA_URL')
    email = os.getenv('JIRA_EMAIL')
    api_token = os.getenv('JIRA_API_TOKEN')

    if not all([jira_url, email, api_token]):
        print("Error: Missing required environment variables")
        sys.exit(1)

    comparator = TypeComparator(jira_url, email, api_token)

    try:
        result = comparator.compare(ticket_urls)

        print("\n" + "="*60)
        print("TYPE COMPARISON RESULT")
        print("="*60)
        print(f"Compared {len(result['types'])} issue types:")
        for t in result['types']:
            detail = result['type_details'][t]
            print(f"  - {t}: {detail['field_count']} fields")

        print(f"\nCommon fields across all types: {len(result['common_fields'])}")
        print(f"Unique fields by type:")
        for t, fields in result['unique_by_type'].items():
            print(f"  - {t}: {len(fields)}")

        # 파일로 저장
        output_file = "type_comparison.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\nFull comparison saved to: {output_file}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
