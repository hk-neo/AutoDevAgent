#!/usr/bin/env python3
"""
특정 이슈 타입의 필드 스키마를 분석하는 도구
"""

import os
import sys
import json
import re

try:
    from jira import JIRA
except ImportError:
    print("Error: jira module not installed. Run: pip install jira")
    sys.exit(1)


def get_type_schema(jira, project_key, issue_type_name):
    """특정 이슈 타입의 필드 스키마 가져오기"""
    # 이슈 타입 ID 찾기
    all_types = jira.issue_types()
    target_type = next((t for t in all_types if t.name == issue_type_name), None)

    if not target_type:
        print(f"Error: Issue type '{issue_type_name}' not found")
        return None

    print(f"Found {issue_type_name} type ID: {target_type.id}")

    # 필드 스키마 가져오기
    jira_url = os.getenv('JIRA_URL')
    createmeta = jira._session.get(
        f"{jira_url}/rest/api/2/issue/createmeta",
        params={
            'projectKeys': project_key,
            'issuetypeIds': target_type.id,
            'expand': 'projects.issuetypes.fields'
        }
    ).json()

    # 필드 분석
    for proj in createmeta.get('projects', []):
        for itype in proj.get('issuetypes', []):
            if itype.get('name') == issue_type_name:
                fields = itype.get('fields', {})

                # 필드 분류
                required_fields = []
                custom_fields = []
                standard_fields = []

                for field_id, field_info in fields.items():
                    field_data = {
                        'id': field_id,
                        'name': field_info.get('name', ''),
                        'type': field_info.get('schema', {}).get('type', 'unknown'),
                        'required': field_info.get('required', False),
                        'custom': field_info.get('schema', {}).get('custom', False),
                        'allowed_values': field_info.get('allowedValues', [])
                    }

                    if field_data['required']:
                        required_fields.append(field_data)
                    elif field_data['custom']:
                        custom_fields.append(field_data)
                    else:
                        standard_fields.append(field_data)

                # 출력
                print(f"\n{'='*60}")
                print(f"{issue_type_name.upper()} FIELD SCHEMA")
                print(f"{'='*60}")
                print(f"Total Fields: {len(fields)}")
                print(f"  - Required: {len(required_fields)}")
                print(f"  - Custom: {len(custom_fields)}")
                print(f"  - Standard: {len(standard_fields)}")

                print(f"\n{'='*60}")
                print("REQUIRED FIELDS")
                print(f"{'='*60}")
                for f in required_fields:
                    print(f"\n  {f['id']}: {f['name']}")
                    print(f"    Type: {f['type']}")

                print(f"\n{'='*60}")
                print("CUSTOM FIELDS")
                print(f"{'='*60}")
                for f in sorted(custom_fields, key=lambda x: x['name']):
                    print(f"\n  {f['id']}: {f['name']}")
                    print(f"    Type: {f['type']}")
                    if f['allowed_values']:
                        opts = [str(v.get('name', v)) for v in f['allowed_values']]
                        if len(opts) <= 10:
                            print(f"    Options: {', '.join(opts)}")
                        else:
                            print(f"    Options: {len(opts)} options")

                # 결과 반환
                return {
                    'issue_type': issue_type_name,
                    'issue_type_id': target_type.id,
                    'project': project_key,
                    'fields': {
                        field_id: field_info
                        for field_id, field_info in fields.items()
                    },
                    'summary': {
                        'total': len(fields),
                        'required': len(required_fields),
                        'custom': len(custom_fields),
                        'standard': len(standard_fields)
                    }
                }

    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze-type-schema.py <jira-ticket-url>")
        print("Example: python analyze-type-schema.py https://domain.atlassian.net/browse/PROJ-123")
        sys.exit(1)

    ticket_url = sys.argv[1]
    jira_url = os.getenv('JIRA_URL')
    jira_email = os.getenv('JIRA_EMAIL')
    jira_token = os.getenv('JIRA_API_TOKEN')

    if not all([jira_url, jira_email, jira_token]):
        print("Error: Missing required environment variables")
        print("Required: JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN")
        sys.exit(1)

    # 티켓 ID 추출
    match = re.search(r'/browse/([A-Z0-9]+-\d+)', ticket_url)
    if not match:
        print(f"Error: Invalid Jira ticket URL: {ticket_url}")
        sys.exit(1)

    ticket_id = match.group(1)
    project_key = ticket_id.split('-')[0]

    # Jira 연결
    jira = JIRA(server=jira_url, basic_auth=(jira_email, jira_token))

    # 티켓의 이슈 타입 확인
    issue = jira.issue(ticket_id)
    issue_type_name = str(issue.fields.issuetype)

    print(f"Analyzing ticket: {ticket_id}")
    print(f"Project: {project_key}")
    print(f"Issue Type: {issue_type_name}")

    # 스키마 분석
    result = get_type_schema(jira, project_key, issue_type_name)

    if result:
        # 파일로 저장
        safe_type_name = issue_type_name.lower().replace(' ', '_')
        output_file = f"data/analysis/{safe_type_name}_fields.json"

        os.makedirs('data/analysis', exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n\nFull schema saved to: {output_file}")


if __name__ == '__main__':
    main()
