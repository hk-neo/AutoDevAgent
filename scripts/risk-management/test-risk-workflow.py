#!/usr/bin/env python3
"""
Risk Management Plugin 테스트 스크립트
Hazard 티켓에 대해 Risk Plugin 활성화 + Risk 값 설정 + 검증

사용법:
  # 특정 티켓에 Risk Plugin 활성화 + 값 설정
  python3 scripts/risk-management/test-risk-workflow.py PLAYG-2005 --severity minor --p1 remote --p2 remote

  # 값만 설정 (활성화 건너뛰기)
  python3 scripts/risk-management/test-risk-workflow.py PLAYG-2005 --severity minor --p1 remote --p2 remote --skip-activate

  # Risk 값 초기화만 (모든 값을 minimal로)
  python3 scripts/risk-management/test-risk-workflow.py PLAYG-2005 --init
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

# Risk Plugin 설정 (README에서 확인)
ENDPOINT = "https://306e01a8-5530-427d-b93a-f91f4898ff16.hello.atlassian-dev.net/x1/p3_h8rdLbpp1-9mjDOXQiqJ4jL4"
AUTHOR = "557058:f58131cb-b67d-43c7-b30d-6b58d40bd077"
RISK_MODEL_KEY = "risk-model-9dc1c741-0858-4a96-65d6-5feaf052da71"

RISK_SETS = {
    'initial': "2f43f135-d043-84bd-4222-46ba4a309738",
    'current': "f957cae9-a34c-30d7-557b-f7f29a414ba5"
}

CLASSIFIERS = {
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


def check_env():
    """환경변수 확인"""
    missing = []
    for name, val in [
        ('JIRA_URL', JIRA_URL),
        ('JIRA_EMAIL', JIRA_EMAIL),
        ('JIRA_API_TOKEN', JIRA_API_TOKEN),
        ('RISK_PLUGIN_AUTH_TOKEN', RISK_AUTH_TOKEN)
    ]:
        if not val:
            missing.append(name)

    if missing:
        print(f"Missing env vars: {', '.join(missing)}")
        sys.exit(1)
    print("Environment: OK")


def get_ticket_info(issue_key):
    """Jira 티켓 정보 조회"""
    url = f"{JIRA_URL}/rest/api/2/issue/{issue_key}"
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    resp = requests.get(url, auth=auth)
    if resp.status_code == 200:
        data = resp.json()
        return {
            'key': data['key'],
            'summary': data['fields']['summary'],
            'issuetype': data['fields']['issuetype']['name'],
            'status': data['fields']['status']['name']
        }
    else:
        print(f"Failed to get ticket: {resp.status_code}")
        return None


def activate_risk_plugin(issue_key):
    """Risk Management Plugin 활성화

    Plugin이 티켓에 연결되려면 초기화가 필요합니다.
    첫 번째 Risk 값을 설정하면 자동으로 활성화됩니다.
    """
    print(f"\n{'='*60}")
    print(f"ACTIVATING RISK PLUGIN ON {issue_key}")
    print(f"{'='*60}")

    # 초기화를 위해 모든 classifier에 대해 첫 값을 설정
    # 이렇게 하면 Risk assessment가 생성됨
    for set_name, set_id in RISK_SETS.items():
        print(f"\n  Initializing {set_name} set...")
        for clf_name, clf_data in CLASSIFIERS.items():
            # 첫 번째 옵션으로 초기화
            first_option_name = list(clf_data['options'].keys())[0]
            first_option_id = clf_data['options'][first_option_name]

            success = set_single_risk_value(
                issue_key, set_id, clf_data['id'], first_option_id,
                f"activate/{clf_name}/{first_option_name}"
            )
            if success:
                print(f"    {clf_name} = {first_option_name}")
            time.sleep(0.3)

    print(f"\n  Plugin activation complete for {issue_key}")


def set_single_risk_value(issue_key, risk_set_id, classifier_id, option_id, label=""):
    """단일 Risk 값 설정"""
    payload = {
        "issueKey": issue_key,
        "author": AUTHOR,
        "riskModelKey": RISK_MODEL_KEY,
        "riskSetId": risk_set_id,
        "classifierValuePayload": {
            "classifierId": classifier_id,
            "optionId": option_id
        }
    }

    headers = {
        'x-trigger-authentication': RISK_AUTH_TOKEN,
        'Content-Type': 'application/json'
    }

    resp = requests.post(ENDPOINT, json=payload, headers=headers)

    status = "OK" if resp.status_code == 200 else f"FAIL({resp.status_code})"
    if resp.status_code != 200:
        print(f"    Response: {resp.text[:200]}")

    return resp.status_code == 200


def set_risk_values(issue_key, severity, p1, p2):
    """Initial + Current Risk Set에 Severity, P1, P2 설정"""
    print(f"\n{'='*60}")
    print(f"SETTING RISK VALUES FOR {issue_key}")
    print(f"{'='*60}")
    print(f"  Severity: {severity}")
    print(f"  P1: {p1}")
    print(f"  P2: {p2}")

    values = {
        'severity': severity,
        'p1': p1,
        'p2': p2
    }

    total = 0
    success = 0

    for set_name, set_id in RISK_SETS.items():
        print(f"\n  [{set_name.upper()}]")
        for clf_name, option_name in values.items():
            clf_data = CLASSIFIERS[clf_name]
            option_id = clf_data['options'].get(option_name)

            if not option_id:
                print(f"    Unknown option: {option_name} for {clf_name}")
                continue

            total += 1
            ok = set_single_risk_value(issue_key, set_id, clf_data['id'], option_id)
            status = "OK" if ok else "FAIL"
            print(f"    {clf_name} = {option_name}: {status}")
            if ok:
                success += 1
            time.sleep(0.3)

    print(f"\n  Result: {success}/{total} values set")
    return success == total


def verify_ticket(issue_key):
    """티켓 상태 확인"""
    info = get_ticket_info(issue_key)
    if info:
        print(f"\n  Ticket: {info['key']}")
        print(f"  Summary: {info['summary']}")
        print(f"  Type: {info['issuetype']}")
        print(f"  Status: {info['status']}")
        return info['issuetype'] == 'Hazard'
    return False


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    issue_key = sys.argv[1]
    skip_activate = '--skip-activate' in sys.argv
    init_mode = '--init' in sys.argv

    print(f"{'='*60}")
    print(f"RISK MANAGEMENT PLUGIN TEST")
    print(f"{'='*60}")
    print(f"Target: {issue_key}")

    # 1. 환경 확인
    check_env()

    # 2. 티켓 확인
    print(f"\n--- Checking ticket ---")
    is_hazard = verify_ticket(issue_key)
    if not is_hazard:
        print("  WARNING: Ticket is not Hazard type!")

    if init_mode:
        # 초기화 모드: 최소값으로 설정
        print("\n--- Init mode: setting minimal values ---")
        activate_risk_plugin(issue_key)
        set_risk_values(issue_key, 'negligible', 'remote', 'remote')
        return

    # 3. 파라미터 파싱
    severity = p1 = p2 = None
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--severity' and i + 1 < len(sys.argv):
            severity = sys.argv[i + 1]; i += 2
        elif sys.argv[i] == '--p1' and i + 1 < len(sys.argv):
            p1 = sys.argv[i + 1]; i += 2
        elif sys.argv[i] == '--p2' and i + 1 < len(sys.argv):
            p2 = sys.argv[i + 1]; i += 2
        else:
            i += 1

    if not severity or not p1 or not p2:
        print("\nNeed --severity, --p1, --p2 values")
        print("Available severity: negligible, minor, serious, critical, catastrophic")
        print("Available P1/P2: improvable, remote, occasional, probable, frequent")
        sys.exit(1)

    # 4. Plugin 활성화
    if not skip_activate:
        print(f"\n--- Step 1: Activating Risk Plugin ---")
        activate_risk_plugin(issue_key)
    else:
        print(f"\n--- Skipping activation ---")

    # 5. Risk 값 설정
    print(f"\n--- Step 2: Setting Risk Values ---")
    ok = set_risk_values(issue_key, severity, p1, p2)

    # 6. 결과
    print(f"\n{'='*60}")
    if ok:
        print(f"SUCCESS: Risk values set for {issue_key}")
        print(f"Check: {JIRA_URL}/browse/{issue_key}")
    else:
        print(f"PARTIAL: Some values may not have been set")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
