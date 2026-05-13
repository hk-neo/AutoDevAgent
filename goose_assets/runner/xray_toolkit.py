#!/usr/bin/env python3
"""
Xray Toolkit - Xray Cloud API와 상호작용하는 도구

사용법:
  export XRAY_CLIENT_ID=...
  export XRAY_CLIENT_SECRET=...

  python3 xray_toolkit.py get_token
  python3 xray_toolkit.py export_cucumber "PLAYG-2384;PLAYG-2385"
  python3 xray_toolkit.py import_results results.json
  python3 xray_toolkit.py get_test_keys PLAYG-2475
"""

import argparse
import json
import os
import sys
import zipfile
import tempfile
from pathlib import Path

import requests

XRAY_AUTH_URL = "https://xray.cloud.getxray.app/api/v2/authenticate"
XRAY_API_BASE = "https://xray.cloud.getxray.app/api/v2"
XRAY_GRAPHQL_URL = f"{XRAY_API_BASE}/graphql"

JIRA_URL = os.getenv("JIRA_URL", "https://neobiotech.atlassian.net")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
XRAY_CLIENT_ID = os.getenv("XRAY_CLIENT_ID")
XRAY_CLIENT_SECRET = os.getenv("XRAY_CLIENT_SECRET")


def get_token():
    if not XRAY_CLIENT_ID or not XRAY_CLIENT_SECRET:
        print("Error: XRAY_CLIENT_ID and XRAY_CLIENT_SECRET must be set", file=sys.stderr)
        sys.exit(1)
    resp = requests.post(
        XRAY_AUTH_URL,
        json={"client_id": XRAY_CLIENT_ID, "client_secret": XRAY_CLIENT_SECRET},
        headers={"Content-Type": "application/json"},
    )
    if resp.status_code == 200:
        return resp.json().strip('"')
    print(f"Error: {resp.status_code} - {resp.text}", file=sys.stderr)
    sys.exit(1)


def jira_headers():
    return {"Accept": "application/json", "Content-Type": "application/json"}


def jira_auth():
    return (JIRA_EMAIL, JIRA_API_TOKEN)


def cmd_get_token(args):
    print(get_token())


def cmd_export_cucumber(args):
    """Cucumber feature 파일 export (zip)"""
    keys = args.keys
    output_dir = args.output or "."
    token = get_token()

    resp = requests.get(
        f"{XRAY_API_BASE}/export/cucumber",
        params={"keys": keys},
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )

    if resp.status_code == 200:
        zip_path = os.path.join(output_dir, "xray-features.zip")
        with open(zip_path, "wb") as f:
            f.write(resp.content)

        # Unzip
        feature_dir = os.path.join(output_dir, "features")
        os.makedirs(feature_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(feature_dir)

        feature_files = [f for f in os.listdir(feature_dir) if f.endswith(".feature")]
        print(json.dumps({
            "zip_path": zip_path,
            "feature_dir": feature_dir,
            "files": feature_files,
            "count": len(feature_files),
        }, indent=2, ensure_ascii=False))
    else:
        print(f"Error: {resp.status_code} - {resp.text}", file=sys.stderr)
        sys.exit(1)


def cmd_import_results(args):
    """테스트 실행 결과 import"""
    token = get_token()

    if args.results_file:
        with open(args.results_file, "r", encoding="utf-8") as f:
            results = json.load(f)
    elif args.results_json:
        results = json.loads(args.results_json)
    else:
        print("Error: provide --results-file or --results-json", file=sys.stderr)
        sys.exit(1)

    resp = requests.post(
        f"{XRAY_API_BASE}/import/execution",
        json=results,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )

    if resp.status_code in (200, 201):
        data = resp.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"Error: {resp.status_code} - {resp.text}", file=sys.stderr)
        sys.exit(1)


def cmd_get_test_keys(args):
    """Test Execution에 연결된 Test 키 목록 조회 (페이지네이션 지원)"""
    te_key = args.test_execution_key
    token = get_token()

    # Get Test Execution issue ID from Jira
    resp = requests.get(
        f"{JIRA_URL}/rest/api/3/issue/{te_key}?fields=summary",
        headers=jira_headers(),
        auth=jira_auth(),
    )
    if resp.status_code != 200:
        print(f"Error fetching issue: {resp.status_code}", file=sys.stderr)
        sys.exit(1)
    issue_id = resp.json()["id"]

    # Paginated GraphQL fetch
    all_results = []
    total = None
    start = 0
    limit = 100

    while total is None or start <= total:
        query = """
        query($issueId: String!, $start: Int!, $limit: Int!) {
            getTestExecution(issueId: $issueId) {
                issueId
                tests(start: $start, limit: $limit) {
                    total
                    results {
                        issueId
                        status { name color }
                        jira(fields: ["key", "summary"])
                    }
                }
            }
        }
        """
        resp = requests.post(
            XRAY_GRAPHQL_URL,
            json={"query": query, "variables": {"issueId": issue_id, "start": start, "limit": limit}},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )

        if resp.status_code != 200:
            print(f"Error: {resp.status_code} - {resp.text}", file=sys.stderr)
            sys.exit(1)

        data = resp.json()
        tests = data.get("data", {}).get("getTestExecution", {}).get("tests", {})
        if total is None:
            total = tests.get("total", 0)
        batch = tests.get("results", [])
        all_results.extend(batch)
        if not batch:
            break
        start += limit

    print(json.dumps({
        "test_execution": te_key,
        "total": total or 0,
        "tests": [
            {
                "key": t.get("jira", {}).get("key", ""),
                "summary": t.get("jira", {}).get("summary", ""),
                "status": t.get("status", {}).get("name", ""),
                "issue_id": t.get("issueId", ""),
            }
            for t in all_results
        ],
    }, indent=2, ensure_ascii=False))


def cmd_get_failed_tests(args):
    """Test Execution에서 FAILED 테스트만 필터링하여 반환"""
    te_key = args.test_execution_key
    token = get_token()

    resp = requests.get(
        f"{JIRA_URL}/rest/api/3/issue/{te_key}?fields=summary",
        headers=jira_headers(),
        auth=jira_auth(),
    )
    if resp.status_code != 200:
        print(f"Error fetching issue: {resp.status_code}", file=sys.stderr)
        sys.exit(1)
    issue_id = resp.json()["id"]

    all_results = []
    total = None
    start = 0
    limit = 100

    while total is None or start <= total:
        query = """
        query($issueId: String!, $start: Int!, $limit: Int!) {
            getTestExecution(issueId: $issueId) {
                tests(start: $start, limit: $limit) {
                    total
                    results {
                        issueId
                        status { name color }
                        jira(fields: ["key", "summary"])
                    }
                }
            }
        }
        """
        resp = requests.post(
            XRAY_GRAPHQL_URL,
            json={"query": query, "variables": {"issueId": issue_id, "start": start, "limit": limit}},
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        )
        if resp.status_code != 200:
            print(f"Error: {resp.status_code} - {resp.text}", file=sys.stderr)
            sys.exit(1)

        data = resp.json()
        tests = data.get("data", {}).get("getTestExecution", {}).get("tests", {})
        if total is None:
            total = tests.get("total", 0)
        batch = tests.get("results", [])
        all_results.extend(batch)
        if not batch:
            break
        start += limit

    failed = [
        {
            "key": t.get("jira", {}).get("key", ""),
            "summary": t.get("jira", {}).get("summary", ""),
            "status": t.get("status", {}).get("name", ""),
        }
        for t in all_results
        if t.get("status", {}).get("name", "").upper() == "FAILED"
    ]

    print(json.dumps({
        "test_execution": te_key,
        "total_tests": total or 0,
        "failed_count": len(failed),
        "failed_tests": failed,
    }, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Xray Cloud API Toolkit")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("get_token", help="Get Xray auth token")

    p_export = sub.add_parser("export_cucumber", help="Export Cucumber features")
    p_export.add_argument("keys", help="Semicolon-separated test keys (e.g. PLAYG-1;PLAYG-2)")
    p_export.add_argument("--output", default=".", help="Output directory")

    p_import = sub.add_parser("import_results", help="Import test execution results")
    p_import.add_argument("--results-file", help="JSON file with results")
    p_import.add_argument("--results-json", help="JSON string with results")

    p_keys = sub.add_parser("get_test_keys", help="Get test keys from Test Execution")
    p_keys.add_argument("test_execution_key", help="Test Execution key (e.g. PLAYG-2475)")

    p_failed = sub.add_parser("get_failed_tests", help="Get failed tests from Test Execution")
    p_failed.add_argument("test_execution_key", help="Test Execution key (e.g. PLAYG-2530)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "get_token": cmd_get_token,
        "export_cucumber": cmd_export_cucumber,
        "import_results": cmd_import_results,
        "get_test_keys": cmd_get_test_keys,
        "get_failed_tests": cmd_get_failed_tests,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
