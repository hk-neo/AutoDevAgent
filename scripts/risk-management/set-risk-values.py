#!/usr/bin/env python3
"""
모든 Risk 값을 5로 설정
Severity, P1, P2를 각각 5로 설정하고 1초씩 대기
"""

import os
import sys
import time
import requests

try:
    from jira import JIRA
except ImportError:
    print("Error: jira module not installed")
    sys.exit(1)

# 설정
JIRA_URL = os.getenv('JIRA_URL')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
RISK_PLUGIN_ENDPOINT = "https://306e01a8-5530-427d-b93a-f91f4898ff16.hello.atlassian-dev.net/x1/p3_h8rdLbpp1-9mjDOXQiqJ4jL4"
AUTH_TOKEN = os.getenv('RISK_PLUGIN_AUTH_TOKEN', 'YTNhY2IyMGFkOWFjZDQ1MmUzZGE2YzJmOGYwODkzYTc3MTYwYzIyMGE1YmNlODVjNjA0OTUyOWQzNjdjNjAwNA==')

# 티켓 설정
if len(sys.argv) > 1:
    ISSUE_KEY = sys.argv[1]
else:
    ISSUE_KEY = "PLAYG-1497"

RISK_MODEL_KEY = "risk-model-9dc1c741-0858-4a96-65d6-5feaf052da71"

# Risk Set IDs
RISK_SETS = {
    'initial': "2f43f135-d043-84bd-4222-46ba4a309738",
    'current': "f957cae9-a34c-30d7-557b-f7f29a414ba5"
}

# Risk 설정값
RISK_SETTINGS = [
    {
        'name': 'Severity',
        'classifier': 'severity',
        'classifier_id': "120dbe93-8a5c-89d9-398c-6fdefc8fa072",
        'option': 'critical',
        'option_id': "587d166e-890a-5123-e179-15bafbd617e1"
    },
    {
        'name': 'P1',
        'classifier': 'p1',
        'classifier_id': "c2c0af5d-74de-e463-ad13-ba80da1b6afd",
        'option': 'probable',
        'option_id': "702cb81f-3bc6-d150-5cc3-daa04d3f0404"
    },
    {
        'name': 'P2',
        'classifier': 'p2',
        'classifier_id': "cdada7bb-cb4a-3b00-260b-5e5227e85a74",
        'option': 'probable',
        'option_id': "bbcbfdd1-0c02-6105-e8e4-f60ae6cacb5c"
    }
]

# Value 2 옵션 IDs
VALUE_2_OPTIONS = [
    {
        'name': 'Severity',
        'classifier': 'severity',
        'classifier_id': "120dbe93-8a5c-89d9-398c-6fdefc8fa072",
        'option': 'minor',
        'option_id': "70ccea9f-a585-d248-dbd0-e6eefcc683e8"
    },
    {
        'name': 'P1',
        'classifier': 'p1',
        'classifier_id': "c2c0af5d-74de-e463-ad13-ba80da1b6afd",
        'option': 'remote',
        'option_id': "2d173a68-c28f-d589-1300-bc127f962810"
    },
    {
        'name': 'P2',
        'classifier': 'p2',
        'classifier_id': "cdada7bb-cb4a-3b00-260b-5e5227e85a74",
        'option': 'remote',
        'option_id': "58257cb8-59e2-5ec7-dd1d-9e966fb13589"
    }
]


def set_risk_value(issue_key, risk_set_id, setting):
    """단일 Risk 값 설정"""

    payload = {
        "issueKey": issue_key,
        "author": "557058:f58131cb-b67d-43c7-b30d-6b58d40bd077",
        "riskModelKey": RISK_MODEL_KEY,
        "riskSetId": risk_set_id,
        "classifierValuePayload": {
            "classifierId": setting['classifier_id'],
            "optionId": setting['option_id']
        }
    }

    headers = {
        'x-trigger-authentication': AUTH_TOKEN,
        'Content-Type': 'application/json'
    }

    print(f"  Setting {setting['name']} to {setting['option']}...")
    print(f"    Classifier ID: {setting['classifier_id']}")
    print(f"    Option ID: {setting['option_id']}")

    response = requests.post(RISK_PLUGIN_ENDPOINT, json=payload, headers=headers)

    if response.status_code == 200:
        print(f"    ✅ Success!")
        return True
    else:
        print(f"    ❌ Failed! Status: {response.status_code}")
        print(f"    Response: {response.text}")
        return False


def set_all_risk_values(issue_key, risk_set_id, settings):
    """모든 Risk 값 설정"""

    success_count = 0
    for i, setting in enumerate(settings, 1):
        print(f"  [{i}/{len(settings)}] {setting['name']}")
        if set_risk_value(issue_key, risk_set_id, setting):
            success_count += 1

        # 다음 설정 전 0.5초 대기
        if i < len(settings):
            print("  Waiting 0.5 second...")
            time.sleep(0.5)

    return success_count


def main():
    print("="*60)
    print("SET RISK VALUES - INITIAL: 4, CURRENT: 2")
    print("="*60)
    print(f"Target Issue: {ISSUE_KEY}")
    print(f"\n⚠️  This will modify the actual ticket!\n")

    print("Initial set (value=4):")
    for setting in RISK_SETTINGS:
        print(f"  - {setting['name']}: {setting['option']} (value=4)")

    print(f"\nCurrent set (value=2):")
    for setting in VALUE_2_OPTIONS:
        print(f"  - {setting['name']}: {setting['option']} (value=2)")

    print(f"\nProceeding in 3 seconds...")
    time.sleep(3)

    total_success = 0
    total_calls = 0

    # 1. Initial risk set: 4로 설정
    print(f"\n{'='*60}")
    print("PHASE 1: INITIAL RISK SET - VALUE = 4")
    print(f"{'='*60}")
    success = set_all_risk_values(ISSUE_KEY, RISK_SETS['initial'], RISK_SETTINGS)
    total_success += success
    total_calls += len(RISK_SETTINGS)

    # Iteration 사이 0.5초 대기
    print(f"\nWaiting 0.5 second between iterations...")
    time.sleep(0.5)

    # 2. Current risk set: 2로 설정
    print(f"\n{'='*60}")
    print("PHASE 2: CURRENT RISK SET - VALUE = 2")
    print(f"{'='*60}")
    success = set_all_risk_values(ISSUE_KEY, RISK_SETS['current'], VALUE_2_OPTIONS)
    total_success += success
    total_calls += len(VALUE_2_OPTIONS)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Completed: {total_success}/{total_calls}")

    if total_success == total_calls:
        print("✅ All risk values set successfully!")
        print(f"   Initial set: value=4")
        print(f"   Current set: value=2")
        print(f"   Check {ISSUE_KEY} in Jira web UI to verify.")
    else:
        print(f"❌ {total_calls - total_success} setting(s) failed")


if __name__ == '__main__':
    main()
