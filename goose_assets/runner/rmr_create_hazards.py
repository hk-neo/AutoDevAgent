#!/usr/bin/env python3
"""
RMR Hazard 일괄 생성 스크립트

Goose가 작성한 hazards.json을 읽어서:
1. risk_helper.py로 Hazard 티켓 생성 + Risk Plugin 활성화 + Risk 값 설정
2. Risk Source 링크 (Hazard → IU/SyRS)
3. Relates 링크 (Hazard → RMR Document)
4. 결과 코멘트용 요약 출력

사용법:
  python3 goose_assets/runner/rmr_create_hazards.py hazards.json --rmr PLAYG-2152 --project PLAYG

  # dry-run (실제 생성 없이 검증만)
  python3 goose_assets/runner/rmr_create_hazards.py hazards.json --rmr PLAYG-2152 --project PLAYG --dry-run

hazards.json 형식:
[
  {
    "summary": "[HAZ-1.1] 영상 렌더링 오류",
    "description": "설명...",
    "harm": "예상되는 Harm",
    "severity": "minor",
    "p1": "occasional",
    "p2": "remote",
    "source_keys": ["PLAYG-1970"]
  },
  ...
]
"""

import json
import os
import sys
import time
import pathlib
import requests

JIRA_URL = os.getenv('JIRA_URL')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')

# risk_helper.py 경로
RISK_HELPER = pathlib.Path(__file__).parent / "risk_helper.py"


def load_hazards(json_path):
    data = json.loads(pathlib.Path(json_path).read_text(encoding='utf-8'))
    if not isinstance(data, list):
        print("Error: hazards.json must be an array of hazard objects")
        sys.exit(1)

    required = ['summary', 'description', 'harm', 'severity', 'p1', 'p2']
    for i, h in enumerate(data):
        for field in required:
            if field not in h:
                print(f"Error: hazard[{i}] missing required field '{field}'")
                sys.exit(1)

    return data


def create_hazard_ticket(project_key, hazard, dry_run=False):
    if dry_run:
        print(f"  [DRY-RUN] Would create: {hazard['summary']}")
        return f"DRY-{i+1:03d}"

    fields = {
        'project': {'key': project_key},
        'summary': hazard['summary'],
        'issuetype': {'name': 'Hazard'},
        'description': hazard['description'],
        'customfield_10148': hazard['harm']
    }

    # JSON 파일 작성
    tmp_path = pathlib.Path('temp_hazard_auto.json')
    tmp_path.write_text(json.dumps(fields, ensure_ascii=False), encoding='utf-8')

    # risk_helper.py로 생성 + Plugin 활성화 + Risk 값 설정
    import subprocess
    cmd = [
        sys.executable, str(RISK_HELPER), 'create', str(tmp_path),
        '--severity', hazard['severity'],
        '--p1', hazard['p1'],
        '--p2', hazard['p2']
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    # 생성된 티켓 키 파싱 (마지막 "Result: KEY-XXX" 라인에서)
    issue_key = None
    for line in result.stdout.strip().split('\n'):
        if line.startswith('Result:'):
            issue_key = line.split(':', 1)[1].strip()

    if not issue_key:
        print(f"  Warning: Could not parse ticket key from output")

    return issue_key


def create_link(link_type, inward_key, outward_key, dry_run=False):
    if dry_run:
        print(f"  [DRY-RUN] Link: {inward_key} <--{link_type}--> {outward_key}")
        return True

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
        return True
    else:
        print(f"  Link failed ({link_type} {inward_key}<->{outward_key}): {resp.status_code} {resp.text[:100]}")
        return False


def check_existing_hazards(rmr_key):
    """RMR에 이미 연결된 Hazard 티켓이 있는지 확인"""
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    resp = requests.get(
        f"{JIRA_URL}/rest/api/2/issue/{rmr_key}?fields=issuelinks",
        auth=auth, headers=headers
    )

    if resp.status_code != 200:
        return []

    existing = []
    for link in resp.json().get('fields', {}).get('issuelinks', []):
        if link.get('type', {}).get('name') == 'Relates':
            if link.get('inwardIssue', {}).get('key') == rmr_key:
                existing.append(link['outwardIssue']['key'])
            elif link.get('outwardIssue', {}).get('key') == rmr_key:
                existing.append(link['inwardIssue']['key'])
        # Blocks 링크도 확인 (이전에 잘못 생성된 경우)
        if link.get('type', {}).get('name') == 'Blocks':
            if link.get('inwardIssue', {}).get('key') == rmr_key:
                existing.append(link['outwardIssue']['key'])

    return existing


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    json_path = sys.argv[1]
    rmr_key = None
    project_key = None
    dry_run = False

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--rmr' and i + 1 < len(sys.argv):
            rmr_key = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--project' and i + 1 < len(sys.argv):
            project_key = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--dry-run':
            dry_run = True
            i += 1
        else:
            i += 1

    if not rmr_key:
        print("Error: --rmr is required (RMR ticket key)")
        sys.exit(1)

    if not project_key:
        project_key = rmr_key.split('-')[0]
        print(f"Project key inferred from RMR: {project_key}")

    # 기존 Hazard 확인
    if not dry_run:
        existing = check_existing_hazards(rmr_key)
        if existing:
            print(f"Warning: RMR already has linked tickets: {existing}")
            print("Skipping to prevent duplicates. Delete existing tickets first if you want to recreate.")
            sys.exit(0)

    # hazards.json 로드
    hazards = load_hazards(json_path)
    print(f"Loaded {len(hazards)} hazards from {json_path}")

    # 순차 생성
    results = []
    for i, hazard in enumerate(hazards):
        print(f"\n--- Hazard {i+1}/{len(hazards)}: {hazard['summary']} ---")

        # 1. 티켓 생성
        issue_key = create_hazard_ticket(project_key, hazard, dry_run)
        if not issue_key:
            print(f"  Skipping links for failed ticket")
            continue

        print(f"  Created: {issue_key}")
        time.sleep(1)

        # 2. Risk Source 링크 (Hazard → IU/SyRS)
        source_keys = hazard.get('source_keys', [])
        for src_key in source_keys:
            create_link('Risk Source', issue_key, src_key, dry_run)
            time.sleep(0.5)

        # 3. Relates 링크 (Hazard → RMR)
        create_link('Relates', issue_key, rmr_key, dry_run)
        time.sleep(0.5)

        results.append({
            'key': issue_key,
            'summary': hazard['summary'],
            'severity': hazard['severity'],
            'p1': hazard['p1'],
            'p2': hazard['p2']
        })

    # 결과 요약
    print(f"\n{'='*50}")
    print(f"총 {len(results)}/{len(hazards)}개 Hazard 생성 완료")
    print(f"{'='*50}")

    # 코멘트용 텍스트 출력
    if results:
        print("\n## 코멘트용 요약 (복사해서 jira_toolkit.py comment에 사용)")
        print(f"!create_subs 완료")
        print(f"Risk Management Report({rmr_key})의 하위 Hazard 티켓 {len(results)}건을 생성하였습니다.")
        print(f"")
        for r in results:
            print(f"- {r['key']}: {r['summary']} (Severity: {r['severity']}, P1: {r['p1']} → P2: {r['p2']})")
        print(f"")
        print(f"모든 티켓은 Risk Source 링크로 관련 요구사항과 연결되었으며, Relates 링크로 RMR과 연결되었습니다.")

    # 결과를 JSON으로도 저장
    result_path = pathlib.Path('hazard_results.json')
    result_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nResults saved to hazard_results.json")


if __name__ == '__main__':
    main()
