#!/usr/bin/env python3
"""
Risk Management 헬퍼
Hazard 티켓 생성 + Risk Management Plugin으로 Risk 값 설정

사용법:
  # Hazard 티켓 생성 + Risk 값 설정 (JSON 파일에서)
  python3 goose_assets/runner/risk_helper.py create hazard.json --severity moderate --p1 remote --p2 remote

  # Risk 값만 설정 (이미 생성된 티켓)
  python3 goose_assets/runner/risk_helper.py set-risk PLAYG-1497 --severity moderate --p1 remote --p2 remote

  # Risk 설정 조회
  python3 goose_assets/runner/risk_helper.py config
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
RISK_AUTH_TOKEN = os.getenv('RISK_PLUGIN_AUTH_TOKEN')

CONFIG_PATH = "config/project-mapping.json"


def activate_risk_panel(issue_key):
    """Risk Management Plugin 패널을 Hazard 티켓에 활성화"""
    import time as _time
    app_id = "306e01a8-5530-427d-b93a-f91f4898ff16"
    config_id = "2a1d023a-d4a5-42c7-91e2-51a05b9eb9be"
    property_key = f"ari:cloud:ecosystem::extension/{app_id}/{config_id}/static/rmp-risk-value-issue-panel"

    url = f"{JIRA_URL}/rest/api/2/issue/{issue_key}/properties/{property_key}"
    payload = [{"added": int(_time.time() * 1000), "id": "44c53f7b", "collapsed": False}]

    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    resp = requests.put(url, json=payload, auth=auth, headers=headers)
    if resp.status_code in (200, 201, 204):
        print(f"  Risk panel activated: OK")
        return True
    else:
        print(f"  Risk panel activation failed: {resp.status_code}")
        return False


def load_risk_config(project_key):
    """project-mapping.json에서 Risk Management 설정 로드, 없으면 하드코딩 fallback"""
    try:
        config = json.loads(pathlib.Path(CONFIG_PATH).read_text(encoding='utf-8'))
        for mapping in config.get('mappings', []):
            if mapping['project_key'] == project_key:
                return mapping.get('settings', {}).get('risk_management')
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # Fallback: hardcoded values for PLAYG
    if project_key == 'PLAYG':
        return {
            'endpoint': "https://306e01a8-5530-427d-b93a-f91f4898ff16.hello.atlassian-dev.net/x1/p3_h8rdLbpp1-9mjDOXQiqJ4jL4",
            'author': "557058:f58131cb-b67d-43c7-b30d-6b58d40bd077",
            'risk_model_key': "risk-model-9dc1c741-0858-4a96-65d6-5feaf052da71",
            'risk_sets': {
                'initial': "2f43f135-d043-84bd-4222-46ba4a309738",
                'current': "f957cae9-a34c-30d7-557b-f7f29a414ba5"
            },
            'classifiers': {
                'severity': {
                    'id': "120dbe93-8a5c-89d9-398c-6fdefc8fa072",
                    'options': {
                        'negligible': "0750b204-3be7-14b2-34c9-5100846e99db",
                        'minor': "70ccea9f-a585-d248-dbd0-e6eefcc683e8",
                        'serious': "a8b765c0-2e55-f6c4-25ff-1a4513c1cfd7",
                        'critical': "587d166e-890a-5123-e179-15bafbd617e1",
                        'catastrophic': "981fbfd5-604d-f9b9-6765-3405a165f401"
                    }
                },
                'p1': {
                    'id': "c2c0af5d-74de-e463-ad13-ba80da1b6afd",
                    'options': {
                        'improvable': "3ac4a3b1-55ef-de93-3452-61c572a905a3",
                        'remote': "2d173a68-c28f-d589-1300-bc127f962810",
                        'occasional': "039596ac-784e-f0ac-50cf-d4d2cc96b096",
                        'probable': "702cb81f-3bc6-d150-5cc3-daa04d3f0404",
                        'frequent': "09fb301a-4448-d8aa-afd2-76d371f501f3"
                    }
                },
                'p2': {
                    'id': "cdada7bb-cb4a-3b00-260b-5e5227e85a74",
                    'options': {
                        'improvable': "7e044b34-25c4-ffae-5237-48eebb190358",
                        'remote': "58257cb8-59e2-5ec7-dd1d-9e966fb13589",
                        'occasional': "6cf5ebce-3b07-69b1-b093-9f0ef9def95c",
                        'probable': "bbcbfdd1-0c02-6105-e8e4-f60ae6cacb5c",
                        'frequent': "e35de539-93d5-f854-c6ed-50067ad8599b"
                    }
                }
            }
        }
    return None


def create_hazard(fields_json_path):
    """Jira API로 Hazard 티켓 생성 + Risk Plugin 활성화"""
    fields = json.loads(pathlib.Path(fields_json_path).read_text(encoding='utf-8'))

    url = f"{JIRA_URL}/rest/api/2/issue"
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {'Content-Type': 'application/json'}

    payload = {'fields': fields}

    resp = requests.post(url, json=payload, auth=auth, headers=headers)
    if resp.status_code == 201:
        data = resp.json()
        issue_key = data['key']
        print(f"Created: {issue_key} - {fields.get('summary', '')}")

        # Risk Plugin 패널 활성화
        time.sleep(0.5)
        activate_risk_panel(issue_key)

        return issue_key
    else:
        print(f"Failed to create: {resp.status_code} {resp.text}")
        return None


def set_risk_value(issue_key, risk_config, classifier_name, option_name, risk_set_id):
    """Risk Management Plugin API로 단일 Risk 값 설정"""
    classifier = risk_config['classifiers'].get(classifier_name)
    if not classifier:
        print(f"  Unknown classifier: {classifier_name}")
        return False

    option_id = classifier['options'].get(option_name)
    if not option_id:
        print(f"  Unknown option: {option_name} for {classifier_name}")
        return False

    payload = {
        "issueKey": issue_key,
        "author": risk_config['author'],
        "riskModelKey": risk_config['risk_model_key'],
        "riskSetId": risk_set_id,
        "classifierValuePayload": {
            "classifierId": classifier['id'],
            "optionId": option_id
        }
    }

    headers = {
        'x-trigger-authentication': RISK_AUTH_TOKEN,
        'Content-Type': 'application/json'
    }

    resp = requests.post(risk_config['endpoint'], json=payload, headers=headers)
    if resp.status_code == 200:
        print(f"  Set {classifier_name}={option_name} on {risk_set_id[:8]}...")
        return True
    else:
        print(f"  Failed: {resp.status_code} {resp.text[:100]}")
        return False


def set_all_risk_values(issue_key, project_key, severity, p1, p2):
    """Initial + Current Risk Set에 대해 Severity, P1, P2 설정"""
    risk_config = load_risk_config(project_key)
    if not risk_config:
        print(f"No risk management config for {project_key}")
        return False

    settings = [
        ('severity', severity),
        ('p1', p1),
        ('p2', p2)
    ]

    total = 0
    success = 0

    for set_name, set_id in risk_config['risk_sets'].items():
        print(f"\nRisk Set: {set_name}")
        for classifier_name, option_name in settings:
            total += 1
            if set_risk_value(issue_key, risk_config, classifier_name, option_name, set_id):
                success += 1
            time.sleep(1.0)

    print(f"\nRisk values: {success}/{total} set")
    return success == total


def show_config(project_key):
    """현재 Risk 설정 출력"""
    risk_config = load_risk_config(project_key)
    if not risk_config:
        print(f"No risk config for {project_key}")
        return

    print(f"Risk Model: {risk_config['risk_model_key']}")
    print(f"Risk Sets:")
    for name, sid in risk_config['risk_sets'].items():
        print(f"  {name}: {sid}")
    print(f"Classifiers:")
    for name, clf in risk_config['classifiers'].items():
        print(f"  {name} (id: {clf['id'][:12]}...)")
        for opt_name, opt_id in clf['options'].items():
            print(f"    {opt_name}: {opt_id[:12]}...")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == 'config':
        project = sys.argv[2] if len(sys.argv) > 2 else 'PLAYG'
        show_config(project)

    elif command == 'create':
        # python3 risk_helper.py create hazard.json --severity moderate --p1 remote --p2 remote
        if len(sys.argv) < 3:
            print("Usage: risk_helper.py create <fields.json> --severity <val> --p1 <val> --p2 <val>")
            sys.exit(1)

        fields_path = sys.argv[2]
        severity = p1 = p2 = None

        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == '--severity' and i + 1 < len(sys.argv):
                severity = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--p1' and i + 1 < len(sys.argv):
                p1 = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--p2' and i + 1 < len(sys.argv):
                p2 = sys.argv[i + 1]
                i += 2
            else:
                i += 1

        # 티켓 생성
        issue_key = create_hazard(fields_path)
        if not issue_key:
            sys.exit(1)

        # 프로젝트 키 추출
        project_key = issue_key.split('-')[0]

        # Risk 값 설정
        if severity and p1 and p2:
            print(f"\nSetting risk values for {issue_key}...")
            set_all_risk_values(issue_key, project_key, severity, p1, p2)

        print(f"\nResult: {issue_key}")

    elif command == 'set-risk':
        # python3 risk_helper.py set-risk PLAYG-1497 --severity moderate --p1 remote --p2 remote
        if len(sys.argv) < 3:
            print("Usage: risk_helper.py set-risk <ISSUE_KEY> --severity <val> --p1 <val> --p2 <val>")
            sys.exit(1)

        issue_key = sys.argv[2]
        project_key = issue_key.split('-')[0]
        severity = p1 = p2 = None

        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == '--severity' and i + 1 < len(sys.argv):
                severity = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--p1' and i + 1 < len(sys.argv):
                p1 = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--p2' and i + 1 < len(sys.argv):
                p2 = sys.argv[i + 1]
                i += 2
            else:
                i += 1

        if severity and p1 and p2:
            set_all_risk_values(issue_key, project_key, severity, p1, p2)
        else:
            print("Need --severity, --p1, --p2 values")

    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == '__main__':
    main()
