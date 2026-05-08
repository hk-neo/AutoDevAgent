#!/usr/bin/env python3
"""
SAD Architecture 일괄 생성 스크립트

Goose가 작성한 temp_architectures.json을 읽어서:
1. Architecture 티켓 생성 (issuetype: Architecture)
2. Implements 링크 (Architecture → Requirement)
3. Relates 링크 (Architecture → SAD Document)

사용법:
  python3 goose_assets/runner/sad_create_architectures.py temp_architectures.json --sad PLAYG-XXXX --project PLAYG

  # dry-run
  python3 goose_assets/runner/sad_create_architectures.py temp_architectures.json --sad PLAYG-XXXX --project PLAYG --dry-run

temp_architectures.json 형식:
{
  "architectures": [
    {
      "summary": "[ARCH-001] DICOM 파서 모듈",
      "description": "설명...",
      "implements": ["PLAYG-2239", "PLAYG-2240"]
    }
  ]
}
"""

import json
import os
import sys
import time
import pathlib
import requests
import functools

print = functools.partial(print, flush=True)

JIRA_URL = os.getenv('JIRA_URL')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')


def load_input(json_path):
    data = json.loads(pathlib.Path(json_path).read_text(encoding='utf-8'))

    if 'architectures' not in data:
        print("Error: missing 'architectures' key")
        sys.exit(1)

    for i, arch in enumerate(data['architectures']):
        if 'summary' not in arch or 'description' not in arch:
            print(f"Error: architecture[{i}] missing summary or description")
            sys.exit(1)

    return data


def text_to_adf(text):
    """일반 텍스트를 Atlassian Document Format으로 변환"""
    paragraphs = []
    for line in text.split('\n'):
        content = [{"type": "text", "text": line}] if line.strip() else []
        paragraphs.append({"type": "paragraph", "content": content})
    return {"type": "doc", "version": 1, "content": paragraphs}


def create_architecture_ticket(project_key, arch):
    """Jira API v3로 직접 Architecture 티켓 생성 (ADF description)"""
    payload = {
        'fields': {
            'project': {'key': project_key},
            'summary': arch['summary'],
            'issuetype': {'name': 'Architecture'},
            'description': text_to_adf(arch['description'])
        }
    }

    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    resp = requests.post(
        f"{JIRA_URL}/rest/api/3/issue",
        json=payload, auth=auth, headers=headers
    )

    if resp.status_code == 201:
        issue_key = resp.json()['key']
        return issue_key
    else:
        print(f"  Error: {resp.status_code} - {resp.text[:200]}")
        return None


def create_link(link_type, inward_key, outward_key):
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    payload = {
        'type': {'name': link_type},
        'inwardIssue': {'key': inward_key},
        'outwardIssue': {'key': outward_key}
    }

    resp = requests.post(
        f"{JIRA_URL}/rest/api/3/issueLink",
        json=payload, auth=auth, headers=headers
    )

    if resp.status_code in (200, 201, 204):
        print(f"  Linked: {outward_key} -[{link_type}]-> {inward_key}")
        return True
    else:
        print(f"  Link failed: {resp.status_code} {resp.text[:80]}")
        return False


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    json_path = sys.argv[1]
    sad_key = None
    project_key = None
    dry_run = False

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--sad' and i + 1 < len(sys.argv):
            sad_key = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--project' and i + 1 < len(sys.argv):
            project_key = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--dry-run':
            dry_run = True
            i += 1
        else:
            i += 1

    if not sad_key:
        print("Error: --sad is required (SAD ticket key)")
        sys.exit(1)

    if not project_key:
        project_key = sad_key.split('-')[0]
        print(f"Project key: {project_key}")

    data = load_input(json_path)
    architectures = data['architectures']

    print(f"Loaded {len(architectures)} architectures")

    if dry_run:
        for i, arch in enumerate(architectures):
            print(f"  [{i+1}/{len(architectures)}] {arch['summary']}")
            print(f"    implements: {arch.get('implements', [])}")
        print(f"\nDry run complete.")
        return

    results = []
    for i, arch in enumerate(architectures):
        print(f"\n[{i+1}/{len(architectures)}] {arch['summary']}")

        # 1. 티켓 생성
        issue_key = create_architecture_ticket(project_key, arch)
        if not issue_key:
            print(f"  FAILED - skipping")
            continue

        print(f"  Created: {issue_key}")
        time.sleep(0.5)

        # 2. Implements 링크 (Architecture implements Requirement)
        # Implements: inward="is implemented by", outward="implements"
        # inwardIssue=Architecture, outwardIssue=Requirement
        for req_key in arch.get('implements', []):
            create_link('Implements', issue_key, req_key)
            time.sleep(0.3)

        # 3. Relates 링크 (Architecture → SAD Document)
        create_link('Relates', issue_key, sad_key)
        time.sleep(0.3)

        results.append({
            'key': issue_key,
            'summary': arch['summary'],
            'implements': arch.get('implements', [])
        })

    # 결과 요약
    print(f"\n{'='*50}")
    print(f"Completed: {len(results)}/{len(architectures)} architectures created")
    print(f"{'='*50}")

    if results:
        print(f"\n## Comment summary")
        print(f"SAD({sad_key}) - {len(results)} Architecture tickets created:")
        for r in results:
            impl_str = ', '.join(r['implements'][:3]) + ('...' if len(r['implements']) > 3 else '')
            print(f"- {r['key']}: {r['summary']} (implements: {impl_str})")

    result_path = pathlib.Path('temp_arch_results.json')
    result_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nResults: temp_arch_results.json")


if __name__ == '__main__':
    main()
