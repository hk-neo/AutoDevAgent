#!/usr/bin/env python3
"""
RMR Hazard 일괄 생성 스크립트

Goose가 작성한 hazards.json을 읽어서:
1. risk_helper 함수 직접 호출로 Hazard 티켓 생성 + Risk Plugin + Risk 값
2. Risk Source 링크 (Hazard arises from IU/SyRS)
3. Relates 링크 (Hazard → RMR Document)
4. 결과 코멘트용 요약 출력

사용법:
  python3 goose_assets/runner/rmr_create_hazards.py temp_hazards.json --rmr PLAYG-2152 --project PLAYG

  # dry-run (실제 생성 없이 검증만)
  python3 goose_assets/runner/rmr_create_hazards.py temp_hazards.json --rmr PLAYG-2152 --project PLAYG --dry-run

temp_hazards.json 형식:
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

# flush 즉시 출력
import functools
print = functools.partial(print, flush=True)

JIRA_URL = os.getenv('JIRA_URL')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')

# risk_helper 함수 직접 임포트
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from risk_helper import create_hazard, set_all_risk_values, activate_risk_panel


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
        print(f"  Linked: {inward_key} <-{link_type}-> {outward_key}")
        return True
    else:
        print(f"  Link failed: {resp.status_code} {resp.text[:80]}")
        return False


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
        print(f"Project key: {project_key}")

    # hazards.json 로드
    hazards = load_hazards(json_path)
    print(f"Loaded {len(hazards)} hazards")

    if dry_run:
        for i, h in enumerate(hazards):
            print(f"  [{i+1}/{len(hazards)}] {h['summary']} (severity={h['severity']}, p1={h['p1']}, p2={h['p2']}, sources={h.get('source_keys', [])})")
        print(f"\nDry run complete. {len(hazards)} hazards validated.")
        return

    # 순차 생성
    results = []
    for i, hazard in enumerate(hazards):
        print(f"\n[{i+1}/{len(hazards)}] {hazard['summary']}")

        # 1. Hazard 티켓 생성 (risk_helper 직접 호출)
        fields = {
            'project': {'key': project_key},
            'summary': hazard['summary'],
            'issuetype': {'name': 'Hazard'},
            'description': hazard['description'],
            'customfield_10148': hazard['harm']
        }
        tmp_path = pathlib.Path('temp_hazard_auto.json')
        tmp_path.write_text(json.dumps(fields, ensure_ascii=False), encoding='utf-8')

        issue_key = create_hazard(str(tmp_path))
        if not issue_key:
            print(f"  FAILED - skipping")
            continue

        # 2. Risk Plugin 활성화 (이미 create_hazard에서 처리됨)
        # 3. Risk 값 설정
        print(f"  Setting risk values...")
        set_all_risk_values(issue_key, project_key, hazard['severity'], hazard['p1'], hazard['p2'])
        time.sleep(0.5)

        # 4. Risk Source 링크 (SyRS gives rise to → Hazard arises from)
        for src_key in hazard.get('source_keys', []):
            create_link('Risk Source', src_key, issue_key)
            time.sleep(0.3)

        # 5. Relates 링크 (Hazard → RMR)
        create_link('Relates', issue_key, rmr_key)
        time.sleep(0.3)

        results.append({
            'key': issue_key,
            'summary': hazard['summary'],
            'severity': hazard['severity'],
            'p1': hazard['p1'],
            'p2': hazard['p2']
        })

        print(f"  Done: {issue_key}")

    # 결과 요약
    print(f"\n{'='*50}")
    print(f"Completed: {len(results)}/{len(hazards)} hazards created")
    print(f"{'='*50}")

    if results:
        print(f"\n## Comment summary")
        print(f"Risk Management Report({rmr_key}) - {len(results)} Hazard tickets created:")
        for r in results:
            print(f"- {r['key']}: {r['summary']} ({r['severity']}, {r['p1']}->{r['p2']})")

    # 결과 JSON 저장
    result_path = pathlib.Path('temp_hazard_results.json')
    result_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nResults: temp_hazard_results.json")


if __name__ == '__main__':
    main()
