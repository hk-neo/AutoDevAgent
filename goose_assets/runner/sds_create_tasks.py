#!/usr/bin/env python3
"""
SDS Task 일괄 생성 스크립트

Bottom-Up 순서로 구현 Task를 생성합니다:
1. Task 티켓 생성 (issuetype: Task)
2. Blocks 링크 (Task → Task, 의존성)
3. Implements 링크 (Task → Detailed Design)
4. Relates 링크 (Task → SDS Document)

사용법:
  python3 goose_assets/runner/sds_create_tasks.py temp_tasks.json --sds PLAYG-XXXX --project PLAYG

  # dry-run
  python3 goose_assets/runner/sds_create_tasks.py temp_tasks.json --sds PLAYG-XXXX --project PLAYG --dry-run

temp_tasks.json 형식:
{
  "tasks": [
    {
      "summary": "[TASK-001] 공유 타입 정의",
      "description": "...",
      "phase": 1,
      "blocks": [],
      "implements_dd": ["PLAYG-XXXX"]
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

    if 'tasks' not in data:
        print("Error: missing 'tasks' key")
        sys.exit(1)

    for i, task in enumerate(data['tasks']):
        if 'summary' not in task or 'description' not in task:
            print(f"Error: task[{i}] missing summary or description")
            sys.exit(1)

    return data


def text_to_adf(text):
    paragraphs = []
    for line in text.split('\n'):
        content = [{"type": "text", "text": line}] if line.strip() else []
        paragraphs.append({"type": "paragraph", "content": content})
    return {"type": "doc", "version": 1, "content": paragraphs}


def create_task_ticket(project_key, task):
    payload = {
        'fields': {
            'project': {'key': project_key},
            'summary': task['summary'],
            'issuetype': {'name': 'Task'},
            'description': text_to_adf(task['description'])
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
    tasks = data['tasks']

    # Phase별 정렬
    tasks.sort(key=lambda t: t.get('phase', 99))

    print(f"Loaded {len(tasks)} tasks")

    if dry_run:
        for i, task in enumerate(tasks):
            phase = task.get('phase', '?')
            blocks = task.get('blocks', [])
            print(f"  [Phase {phase}] {task['summary']}")
            if blocks:
                print(f"    blocks: {blocks}")
        print(f"\nDry run complete.")
        return

    # 순환 의존성 검사
    summary_to_index = {}
    for i, task in enumerate(tasks):
        summary_to_index[task['summary']] = i

    # 1. Task 티켓 생성 (Phase 순서대로)
    results = []
    summary_to_key = {}

    for i, task in enumerate(tasks):
        phase = task.get('phase', '?')
        print(f"\n[Phase {phase}] [{i+1}/{len(tasks)}] {task['summary']}")

        issue_key = create_task_ticket(project_key, task)
        if not issue_key:
            print(f"  FAILED - skipping")
            continue

        print(f"  Created: {issue_key}")
        summary_to_key[task['summary']] = issue_key
        time.sleep(0.5)

        # Relates 링크 (Task → SDS Document)
        create_link('Relates', issue_key, sds_key)
        time.sleep(0.3)

        # Implements 링크 (Task → Detailed Design)
        for dd_key in task.get('implements_dd', []):
            create_link('Implements', issue_key, dd_key)
            time.sleep(0.3)

        results.append({
            'key': issue_key,
            'summary': task['summary'],
            'phase': task.get('phase', '?'),
            'blocks': task.get('blocks', []),
            'implements_dd': task.get('implements_dd', [])
        })

    # 2. Blocks 링크 (의존성) — 모든 티켓 생성 후 연결
    print(f"\n--- Creating dependency links ---")
    for r in results:
        for block_summary in r['blocks']:
            blocked_by_key = summary_to_key.get(block_summary)
            if blocked_by_key:
                # Blocks: inwardIssue=후행Task, outwardIssue=선행Task
                # 후행 Task "is blocked by" 선행 Task
                create_link('Blocks', r['key'], blocked_by_key)
                time.sleep(0.3)
            else:
                print(f"  Warning: {block_summary} not found, skipping blocks link")

    # 결과 요약
    print(f"\n{'='*50}")
    print(f"Completed: {len(results)}/{len(tasks)} tasks created")
    print(f"{'='*50}")

    if results:
        # Phase별 그룹화
        phases = {}
        for r in results:
            p = r['phase']
            if p not in phases:
                phases[p] = []
            phases[p].append(r)

        print(f"\n## Comment summary")
        print(f"SDS({sds_key}) - {len(results)} Task tickets created:")
        for phase in sorted(phases.keys()):
            print(f"\n### Phase {phase}")
            for r in phases[phase]:
                impl_str = ', '.join(r['implements_dd'][:2])
                print(f"- {r['key']}: {r['summary']}" + (f" (→ {impl_str})" if impl_str else ""))

        print(f"\n### Dependency Graph")
        for r in results:
            if r['blocks']:
                blocks_str = ', '.join(r['blocks'][:3])
                print(f"- {r['key']} blocked by: {blocks_str}")

    result_path = pathlib.Path('temp_task_results.json')
    result_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nResults: temp_task_results.json")


if __name__ == '__main__':
    main()
