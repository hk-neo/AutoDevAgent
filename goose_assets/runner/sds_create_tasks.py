#!/usr/bin/env python3
"""
SDS Task 생성 스크립트

Task를 하나씩 생성하고, 마지막에 의존성을 연결합니다.

사용법:
  # Task 1개 생성
  python3 goose_assets/runner/sds_create_tasks.py add \
    --sds PLAYG-2280 --project PLAYG \
    --summary "[TASK-001] 공유 타입 정의" \
    --phase 1 \
    --blocks "" \
    --dd PLAYG-2352

  # description이 길면 파일로 전달
  python3 goose_assets/runner/sds_create_tasks.py add \
    --sds PLAYG-2280 --project PLAYG \
    --summary "[TASK-001] 공유 타입 정의" \
    --desc-file /tmp/task_desc.txt \
    --phase 1 --blocks "" --dd PLAYG-2352

  # 모든 Task 생성 후 의존성 연결
  python3 goose_assets/runner/sds_create_tasks.py link --project PLAYG

  # 등록된 Task 목록 확인
  python3 goose_assets/runner/sds_create_tasks.py list

  # 결과 코멘트용 요약 출력
  python3 goose_assets/runner/sds_create_tasks.py summary --sds PLAYG-2280
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

REGISTRY_FILE = pathlib.Path('temp_task_registry.json')


def load_registry():
    if REGISTRY_FILE.exists():
        return json.loads(REGISTRY_FILE.read_text(encoding='utf-8'))
    return {"tasks": []}


def save_registry(reg):
    REGISTRY_FILE.write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding='utf-8')


def text_to_adf(text):
    paragraphs = []
    for line in text.split('\n'):
        content = [{"type": "text", "text": line}] if line.strip() else []
        paragraphs.append({"type": "paragraph", "content": content})
    return {"type": "doc", "version": 1, "content": paragraphs}


def create_jira_ticket(project_key, summary, description):
    payload = {
        'fields': {
            'project': {'key': project_key},
            'summary': summary,
            'issuetype': {'name': 'Task'},
            'description': text_to_adf(description)
        }
    }

    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    resp = requests.post(
        f"{JIRA_URL}/rest/api/3/issue",
        json=payload, auth=auth, headers=headers
    )

    if resp.status_code == 201:
        return resp.json()['key']
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


def cmd_add(args):
    """Task 1개 생성"""
    sds_key = None
    project_key = None
    summary = None
    desc_file = None
    phase = 0
    blocks_str = ""
    dd_keys = []

    i = 0
    while i < len(args):
        if args[i] == '--sds' and i + 1 < len(args):
            sds_key = args[i + 1]; i += 2
        elif args[i] == '--project' and i + 1 < len(args):
            project_key = args[i + 1]; i += 2
        elif args[i] == '--summary' and i + 1 < len(args):
            summary = args[i + 1]; i += 2
        elif args[i] == '--desc-file' and i + 1 < len(args):
            desc_file = args[i + 1]; i += 2
        elif args[i] == '--phase' and i + 1 < len(args):
            phase = int(args[i + 1]); i += 2
        elif args[i] == '--blocks' and i + 1 < len(args):
            blocks_str = args[i + 1]; i += 2
        elif args[i] == '--dd' and i + 1 < len(args):
            dd_keys.append(args[i + 1]); i += 2
        else:
            i += 1

    if not summary:
        print("Error: --summary is required")
        sys.exit(1)
    if not sds_key:
        print("Error: --sds is required")
        sys.exit(1)
    if not project_key:
        project_key = sds_key.split('-')[0]

    # description 읽기
    if desc_file:
        description = pathlib.Path(desc_file).read_text(encoding='utf-8')
    else:
        description = summary

    blocks = [b.strip() for b in blocks_str.split(',') if b.strip()] if blocks_str else []

    # Jira 티켓 생성
    print(f"Creating: {summary}")
    issue_key = create_jira_ticket(project_key, summary, description)
    if not issue_key:
        print(f"  FAILED")
        sys.exit(1)

    print(f"  Created: {issue_key}")
    time.sleep(0.5)

    # Relates 링크 (Task → SDS)
    create_link('Relates', issue_key, sds_key)
    time.sleep(0.3)

    # Implements 링크 (Task → Detailed Design)
    for dd_key in dd_keys:
        create_link('Implements', issue_key, dd_key)
        time.sleep(0.3)

    # Registry에 기록
    reg = load_registry()
    reg['tasks'].append({
        'key': issue_key,
        'summary': summary,
        'phase': phase,
        'blocks': blocks,
        'implements_dd': dd_keys,
        'sds': sds_key
    })
    save_registry(reg)

    print(f"  Registered: {issue_key} (Phase {phase}, blocks: {blocks})")


def cmd_link(args):
    """Registry의 모든 Task 간 Blocks 링크 생성"""
    project_key = None

    i = 0
    while i < len(args):
        if args[i] == '--project' and i + 1 < len(args):
            project_key = args[i + 1]; i += 2
        else:
            i += 1

    reg = load_registry()
    if not reg['tasks']:
        print("No tasks in registry")
        return

    summary_to_key = {t['summary']: t['key'] for t in reg['tasks']}

    print(f"Creating dependency links for {len(reg['tasks'])} tasks...")

    for task in reg['tasks']:
        for block_summary in task['blocks']:
            blocked_by_key = summary_to_key.get(block_summary)
            if blocked_by_key:
                create_link('Blocks', task['key'], blocked_by_key)
                time.sleep(0.3)
            else:
                print(f"  Warning: '{block_summary}' not found in registry")

    print(f"\nDependency links created.")


def cmd_list(args):
    """Registry의 Task 목록 출력"""
    reg = load_registry()
    if not reg['tasks']:
        print("No tasks in registry")
        return

    phases = {}
    for t in reg['tasks']:
        p = t.get('phase', '?')
        if p not in phases:
            phases[p] = []
        phases[p].append(t)

    for phase in sorted(phases.keys()):
        print(f"\nPhase {phase}:")
        for t in phases[phase]:
            blocks_str = ', '.join(t.get('blocks', []))
            print(f"  {t['key']}: {t['summary']}" + (f" (blocks: {blocks_str})" if blocks_str else ""))


def cmd_summary(args):
    """코멘트용 요약 출력"""
    sds_key = None
    i = 0
    while i < len(args):
        if args[i] == '--sds' and i + 1 < len(args):
            sds_key = args[i + 1]; i += 2
        else:
            i += 1

    reg = load_registry()
    if not reg['tasks']:
        print("No tasks in registry")
        return

    phases = {}
    for t in reg['tasks']:
        p = t.get('phase', '?')
        if p not in phases:
            phases[p] = []
        phases[p].append(t)

    total = len(reg['tasks'])
    print(f"SDS({sds_key}) - {total} Task tickets created:\n")

    phase_names = {1: "Foundation", 2: "Data Layer", 3: "Rendering Engine", 4: "Features", 5: "UI Shell", 6: "Security & Polish"}

    for phase in sorted(phases.keys()):
        name = phase_names.get(phase, f"Phase {phase}")
        print(f"### Phase {phase}: {name}")
        for t in phases[phase]:
            dd_str = ', '.join(t.get('implements_dd', [])[:2])
            print(f"- {t['key']}: {t['summary']}" + (f" (→ {dd_str})" if dd_str else ""))
        print()

    print("### Dependencies")
    for t in reg['tasks']:
        if t.get('blocks'):
            print(f"- {t['key']} blocked by: {', '.join(t['blocks'])}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    subcmd = sys.argv[1]
    args = sys.argv[2:]

    if subcmd == 'add':
        cmd_add(args)
    elif subcmd == 'link':
        cmd_link(args)
    elif subcmd == 'list':
        cmd_list(args)
    elif subcmd == 'summary':
        cmd_summary(args)
    else:
        print(f"Unknown command: {subcmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
