#!/usr/bin/env python3
"""
Jira 티켓 필드 분석 도구

주어진 Jira 티켓 URL에서 필드 정보를 수집하고 분석합니다.
이 정보는 Goose 스킬에서 Jira 필드를 업데이트할 때 사용됩니다.
"""

import json
import os
import re
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    from jira import JIRA
except ImportError:
    print("Error: jira library not installed. Run: pip install jira")
    sys.exit(1)


class JiraFieldAnalyzer:
    def __init__(self, jira_url: str, email: str, api_token: str):
        self.jira_url = jira_url
        self.email = email
        self.api_token = api_token
        self.jira = JIRA(server=jira_url, basic_auth=(email, api_token))

    def parse_ticket_url(self, url: str) -> Optional[str]:
        """Jira 티켓 URL에서 티켓 ID 추출"""
        # URL 패턴: https://domain.atlassian.net/browse/PROJ-123
        pattern = r'/browse/([A-Z0-9]+-\d+)'
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """티켓 정보 가져오기"""
        issue = self.jira.issue(ticket_id, fields='*all')
        return {
            'id': issue.key,
            'summary': issue.fields.summary,
            'description': issue.fields.description or '',
            'status': str(issue.fields.status),
            'issuetype': str(issue.fields.issuetype),
            'priority': str(issue.fields.priority) if issue.fields.priority else None,
            'assignee': str(issue.fields.assignee) if issue.fields.assignee else None,
            'reporter': str(issue.fields.reporter) if issue.fields.reporter else None,
            'created': str(issue.fields.created) if issue.fields.created else None,
            'updated': str(issue.fields.updated) if issue.fields.updated else None,
        }

    def analyze_fields(self, ticket_id: str) -> Dict[str, Any]:
        """티켓의 모든 필드 분석"""
        issue = self.jira.issue(ticket_id, fields='*all')

        # 모든 필드 정보 수집
        all_fields = self.jira.fields()

        # 티켓에서 사용 중인 필드 식별
        used_fields = {}

        for field in all_fields:
            field_id = field['id']
            field_name = field['name']
            is_custom = field['custom']

            # 티켓에서 해당 필드의 값 확인
            raw_value = getattr(issue.fields, field_id, None)

            if raw_value is not None:
                value = self._format_field_value(raw_value)
                used_fields[field_id] = {
                    'id': field_id,
                    'name': field_name,
                    'is_custom': is_custom,
                    'type': field.get('schema', {}).get('type', 'unknown'),
                    'value': value,
                    'has_value': True
                }
            elif is_custom:
                # 커스텀 필드는 값이 없어도 기록
                used_fields[field_id] = {
                    'id': field_id,
                    'name': field_name,
                    'is_custom': True,
                    'type': field.get('schema', {}).get('type', 'unknown'),
                    'value': None,
                    'has_value': False
                }

        return used_fields

    def _format_field_value(self, value: Any) -> Any:
        """필드 값을 JSON 직렬화 가능한 형태로 변환"""
        if value is None:
            return None
        elif hasattr(value, 'key'):
            # Jira Issue 객체
            return {
                'type': 'issue',
                'key': value.key,
                'summary': getattr(value, 'fields', {}).get('summary', '')
            }
        elif hasattr(value, 'name'):
            # User 또는 Select 옵션
            return {
                'type': 'named',
                'name': value.name,
                'id': getattr(value, 'id', None)
            }
        elif isinstance(value, list):
            return [self._format_field_value(v) for v in value]
        else:
            return value

    def get_field_definitions(self, ticket_id: str) -> Dict[str, Any]:
        """티켓 타입에 따른 필드 정의 수집"""
        issue = self.jira.issue(ticket_id)
        issue_type = str(issue.fields.issuetype)

        # 해당 이슈 타입의 필드 스키마 가져오기
        createmeta = self.jira.createmeta(projectKeys=[issue.key.split('-')[0]],
                                          issuetypeNames=[issue_type])

        field_definitions = {}
        for project_data in createmeta['projects']:
            for issue_type_data in project_data['issuetypes']:
                for field in issue_type_data['fields']:
                    field_definitions[field['key']] = {
                        'id': field['key'],
                        'name': field['name'],
                        'is_custom': field.get('custom', False),
                        'type': field.get('schema', {}).get('type', 'unknown'),
                        'required': field.get('required', False),
                        'allowed_values': self._extract_allowed_values(field)
                    }

        return field_definitions

    def _extract_allowed_values(self, field: Dict[str, Any]) -> Optional[List[str]]:
        """필드의 허용된 값 목록 추출"""
        allowed = field.get('allowedValues', [])
        if not allowed:
            return None

        result = []
        for value in allowed:
            if isinstance(value, dict):
                if 'name' in value:
                    result.append(value['name'])
                elif 'value' in value:
                    result.append(value['value'])
            else:
                result.append(str(value))

        return result if result else None

    def analyze(self, ticket_url: str) -> Dict[str, Any]:
        """티켓 전체 분석 수행"""
        ticket_id = self.parse_ticket_url(ticket_url)
        if not ticket_id:
            raise ValueError(f"Invalid Jira ticket URL: {ticket_url}")

        print(f"Analyzing ticket: {ticket_id}")

        # 기본 티켓 정보
        ticket_info = self.get_ticket(ticket_id)

        # 필드 분석
        fields = self.analyze_fields(ticket_id)

        # 필드 정의
        field_definitions = self.get_field_definitions(ticket_id)

        return {
            'analyzed_at': datetime.now().isoformat(),
            'ticket': ticket_info,
            'fields': fields,
            'field_definitions': field_definitions,
            'summary': {
                'total_fields': len(fields),
                'custom_fields': sum(1 for f in fields.values() if f['is_custom']),
                'fields_with_values': sum(1 for f in fields.values() if f['has_value']),
            }
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze-ticket.py <jira-ticket-url>")
        print("Environment variables: JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN")
        sys.exit(1)

    ticket_url = sys.argv[1]
    jira_url = os.getenv('JIRA_URL')
    email = os.getenv('JIRA_EMAIL')
    api_token = os.getenv('JIRA_API_TOKEN')

    if not all([jira_url, email, api_token]):
        print("Error: Missing required environment variables")
        print("Required: JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN")
        sys.exit(1)

    analyzer = JiraFieldAnalyzer(jira_url, email, api_token)

    try:
        result = analyzer.analyze(ticket_url)

        # 결과 출력
        print("\n" + "="*50)
        print("ANALYSIS RESULT")
        print("="*50)
        print(f"Ticket: {result['ticket']['id']}")
        print(f"Type: {result['ticket']['issuetype']}")
        print(f"Summary: {result['ticket']['summary']}")
        print(f"\nFields: {result['summary']['total_fields']}")
        print(f"  - Custom: {result['summary']['custom_fields']}")
        print(f"  - With values: {result['summary']['fields_with_values']}")

        # 파일로 저장
        output_file = f"ticket_analysis_{result['ticket']['id']}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\nFull analysis saved to: {output_file}")

    except Exception as e:
        print(f"Error analyzing ticket: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
