#!/usr/bin/env python3
"""
SDS Module 일괄 생성 스크립트

Goose가 작성한 temp_modules.json을 읽어서:
1. Module 티켓 생성 (issuetype: Task)
2. Implements 링크 (Module → Architecture)
3. Relates 링크 (Module → SDS Document)

사용법:
  python3 goose_assets/runner/sds_create_modules.py temp_modules.json --sds PLAYG-XXXX --project PLAYG

  # dry-run
  python3 goose_assets/runner/sds_create_modules.py temp_modules.json --sds PLAYG-XXXX --project PLAYG --dry-run

temp_modules.json 형식:
{
  "modules": [
    {
      "summary": "[MOD-001] DICOM 파일 파서",
      "description": "상세 설계 내용...",
      "implements": ["PLAYG-2299"],
      "implements_req": ["PLAYG-2239", "PLAYG-2240"]
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

    if 'modules' not in data:
        print("Error: missing 'modules' key")
        sys.exit(1)

    for i, mod in enumerate(data['modules']):
        if 'summary' not in mod or 'description' not in mod:
            print(f"Error: module[{i}] missing summary or description")
            sys.exit(1)

    return data


def text_to_adf(text):
    paragraphs = []
    for line in text.split('\n'):
        content = [{"type": "text", "text": line}] if line.strip() else []
        paragraphs.append({"type": "paragraph", "content": content})
    return {"type": "doc", "version": 1, "content": paragraphs}


def create_module_ticket(project_key, mod):
    payload = {
        'fields': {
            'project': {'key': project_key},
            'summary': mod['summary'],
            'issuetype': {'name': 'Detailed Design'},
            'description': text_to_adf(mod['description'])
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
    sds_key = None
    project_key = None
    dry_run = False

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--sds' and i + 1 < len(sys.argv):
            sds_key = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--project' and i + 1 < len(sys.argv):
            project_key = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--dry-run':
            dry_run = True
            i += 1
        else:
            i += 1

    if not sds_key:
        print("Error: --sds is required (SDS ticket key)")
        sys.exit(1)

    if not project_key:
        project_key = sds_key.split('-')[0]
        print(f"Project key: {project_key}")

    data = load_input(json_path)
    modules = data['modules']

    print(f"Loaded {len(modules)} modules")

    if dry_run:
        for i, mod in enumerate(modules):
            print(f"  [{i+1}/{len(modules)}] {mod['summary']}")
            print(f"    implements: {mod.get('implements', [])}")
            print(f"    implements_req: {mod.get('implements_req', [])}")
        print(f"\nDry run complete.")
        return

    results = []
    for i, mod in enumerate(modules):
        print(f"\n[{i+1}/{len(modules)}] {mod['summary']}")

        # 1. 티켓 생성
        issue_key = create_module_ticket(project_key, mod)
        if not issue_key:
            print(f"  FAILED - skipping")
            continue

        print(f"  Created: {issue_key}")
        time.sleep(0.5)

        # 2. Implements 링크 (Module implements Architecture)
        for arch_key in mod.get('implements', []):
            create_link('Implements', issue_key, arch_key)
            time.sleep(0.3)

        # 3. Implements 링크 (Module implements Requirement — 근거 추적)
        for req_key in mod.get('implements_req', []):
            create_link('Implements', issue_key, req_key)
            time.sleep(0.3)

        # 4. Relates 링크 (Module → SDS Document)
        create_link('Relates', issue_key, sds_key)
        time.sleep(0.3)

        results.append({
            'key': issue_key,
            'summary': mod['summary'],
            'implements': mod.get('implements', []),
            'implements_req': mod.get('implements_req', [])
        })

    # 결과 요약
    print(f"\n{'='*50}")
    print(f"Completed: {len(results)}/{len(modules)} modules created")
    print(f"{'='*50}")

    if results:
        print(f"\n## Comment summary")
        print(f"SDS({sds_key}) - {len(results)} Module tickets created:")
        for r in results:
            impl_str = ', '.join(r['implements'][:3]) + ('...' if len(r['implements']) > 3 else '')
            req_str = ', '.join(r['implements_req'][:3]) + ('...' if len(r['implements_req']) > 3 else '')
            print(f"- {r['key']}: {r['summary']} (arch: {impl_str}, req: {req_str})")

    result_path = pathlib.Path('temp_mod_results.json')
    result_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nResults: temp_mod_results.json")


if __name__ == '__main__':
    main()
