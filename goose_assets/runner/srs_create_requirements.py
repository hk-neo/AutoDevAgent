#!/usr/bin/env python3
"""
SRS Requirement 일괄 생성 스크립트

Goose가 작성한 temp_requirements.json을 읽어서:
1. Requirement 티켓 생성 (issuetype: Requirement)
2. Mitigates 링크 (Requirement → Hazard)
3. Relates 링크 (Requirement → SRS Document)
4. Hazard Current Risk P2 값 업데이트 (완화 조치 반영)

사용법:
  python3 goose_assets/runner/srs_create_requirements.py temp_requirements.json --srs PLAYG-XXXX --project PLAYG

  # dry-run
  python3 goose_assets/runner/srs_create_requirements.py temp_requirements.json --srs PLAYG-XXXX --project PLAYG --dry-run

temp_requirements.json 형식:
{
  "requirements": [
    {
      "summary": "[REQ-001] DICOM 파싱 유효성 검증",
      "description": "설명...",
      "mitigates": ["PLAYG-2195", "PLAYG-2196"],
      "implements": ["PLAYG-1970"]
    }
  ],
  "hazard_risk_updates": {
    "PLAYG-2195": {"p2": "remote"},
    "PLAYG-2196": {"p2": "remote"}
  }
}
"""

import json
import os
import sys
import time
import pathlib
import requests
import subprocess
import functools

# flush 즉시 출력
print = functools.partial(print, flush=True)

JIRA_URL = os.getenv('JIRA_URL')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')

# risk_helper 직접 임포트
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from risk_helper import load_risk_config, set_risk_value


def load_input(json_path):
    data = json.loads(pathlib.Path(json_path).read_text(encoding='utf-8'))

    if 'requirements' not in data:
        print("Error: missing 'requirements' key")
        sys.exit(1)

    for i, req in enumerate(data['requirements']):
        if 'summary' not in req or 'description' not in req:
            print(f"Error: requirement[{i}] missing summary or description")
            sys.exit(1)

    return data


def create_requirement_ticket(project_key, req):
    """jira_toolkit.py로 Requirement 티켓 생성"""
    fields = {
        'project': {'key': project_key},
        'summary': req['summary'],
        'issuetype': {'name': 'Requirement'},
        'description': req['description']
    }

    tmp_path = pathlib.Path('temp_req_auto.json')
    tmp_path.write_text(json.dumps(fields, ensure_ascii=False), encoding='utf-8')

    result = subprocess.run(
        [sys.executable, 'goose_assets/runner/jira_toolkit.py', 'create', str(tmp_path)],
        capture_output=True, text=True
    )

    issue_key = None
    for line in result.stdout.strip().split('\n'):
        if 'Created:' in line or 'key' in line.lower():
            parts = line.strip().split()
            for p in parts:
                if '-' in p and any(c.isdigit() for c in p):
                    issue_key = p.rstrip(',')
                    break

    if not issue_key and result.stdout.strip():
        last_line = result.stdout.strip().split('\n')[-1].strip()
        if '-' in last_line and any(c.isdigit() for c in last_line):
            issue_key = last_line

    if result.stderr:
        print(f"  stderr: {result.stderr[:100]}")

    return issue_key


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


def update_hazard_p2(hazard_key, new_p2, project_key):
    """Hazard의 Current Risk P2만 업데이트"""
    risk_config = load_risk_config(project_key)
    if not risk_config:
        print(f"  No risk config for {project_key}, skipping P2 update")
        return False

    current_set_id = risk_config['risk_sets']['current']
    ok = set_risk_value(hazard_key, risk_config, 'p2', new_p2, current_set_id)
    if ok:
        print(f"  Updated {hazard_key} Current P2 -> {new_p2}")
    return ok


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    json_path = sys.argv[1]
    srs_key = None
    project_key = None
    dry_run = False

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--srs' and i + 1 < len(sys.argv):
            srs_key = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--project' and i + 1 < len(sys.argv):
            project_key = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--dry-run':
            dry_run = True
            i += 1
        else:
            i += 1

    if not srs_key:
        print("Error: --srs is required (SRS ticket key)")
        sys.exit(1)

    if not project_key:
        project_key = srs_key.split('-')[0]
        print(f"Project key: {project_key}")

    data = load_input(json_path)
    requirements = data['requirements']
    risk_updates = data.get('hazard_risk_updates', {})

    print(f"Loaded {len(requirements)} requirements, {len(risk_updates)} hazard risk updates")

    if dry_run:
        for i, req in enumerate(requirements):
            print(f"  [{i+1}/{len(requirements)}] {req['summary']}")
            print(f"    mitigates: {req.get('mitigates', [])}")
        for haz_key, upd in risk_updates.items():
            print(f"  {haz_key}: P2 -> {upd['p2']}")
        print(f"\nDry run complete.")
        return

    # 1. Requirement 티켓 생성 + 링크
    results = []
    for i, req in enumerate(requirements):
        print(f"\n[{i+1}/{len(requirements)}] {req['summary']}")

        # 티켓 생성
        issue_key = create_requirement_ticket(project_key, req)
        if not issue_key:
            print(f"  FAILED - skipping")
            continue

        print(f"  Created: {issue_key}")
        time.sleep(0.5)

        # Mitigates 링크 (Requirement mitigates Hazard)
        # Mitigates: inward="is mitigated by", outward="mitigates"
        # inwardIssue=Hazard, outwardIssue=Requirement
        for haz_key in req.get('mitigates', []):
            create_link('Mitigates', haz_key, issue_key)
            time.sleep(0.3)

        # Implements 링크 (Requirement implements System Requirement)
        # Implements: inward="is implemented by", outward="implements"
        # inwardIssue=Requirement, outwardIssue=SyRS
        for syrs_key in req.get('implements', []):
            create_link('Implements', issue_key, syrs_key)
            time.sleep(0.3)

        # Relates 링크 (Requirement → SRS Document)
        create_link('Relates', issue_key, srs_key)
        time.sleep(0.3)

        results.append({
            'key': issue_key,
            'summary': req['summary'],
            'mitigates': req.get('mitigates', []),
            'implements': req.get('implements', [])
        })

    # 2. Hazard Current Risk P2 업데이트
    if risk_updates:
        print(f"\n--- Updating Hazard Risk Values ---")
        for haz_key, upd in risk_updates.items():
            update_hazard_p2(haz_key, upd['p2'], project_key)
            time.sleep(0.5)

    # 결과 요약
    print(f"\n{'='*50}")
    print(f"Completed: {len(results)}/{len(requirements)} requirements created")
    print(f"Risk updates: {len(risk_updates)} hazards")
    print(f"{'='*50}")

    if results:
        print(f"\n## Comment summary")
        print(f"SRS({srs_key}) - {len(results)} Requirement tickets created:")
        for r in results:
            mit_str = ', '.join(r['mitigates'][:3]) + ('...' if len(r['mitigates']) > 3 else '')
            print(f"- {r['key']}: {r['summary']} (mitigates: {mit_str})")
        if risk_updates:
            print(f"\nHazard Risk Updates:")
            for haz_key, upd in risk_updates.items():
                print(f"- {haz_key}: Current P2 -> {upd['p2']}")

    # 결과 JSON 저장
    result_path = pathlib.Path('temp_req_results.json')
    result_path.write_text(json.dumps({
        'results': results,
        'risk_updates': risk_updates
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nResults: temp_req_results.json")


if __name__ == '__main__':
    main()
