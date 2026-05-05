#!/usr/bin/env python3
"""
Jira 보드의 모든 티켓 정보를 백업합니다.
"""

import argparse
import json
import os
from pathlib import Path

import requests

JIRA_URL = os.getenv("JIRA_URL", "https://neobiotech.atlassian.net")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")


def get_headers():
    if not JIRA_EMAIL or not JIRA_API_TOKEN:
        raise ValueError("JIRA_EMAIL and JIRA_API_TOKEN must be set")
    return {
        "Accept": "application/json"
    }


def get_auth():
    return (JIRA_EMAIL, JIRA_API_TOKEN)


def get_board_tickets(board_id):
    """보드의 모든 티켓을 가져옵니다."""
    tickets = []
    start_at = 0
    max_results = 50

    while True:
        url = f"{JIRA_URL}/rest/agile/1.0/board/{board_id}/issue?startAt={start_at}&maxResults={max_results}"

        response = requests.get(url, headers=get_headers(), auth=get_auth())

        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            break

        data = response.json()
        tickets.extend(data.get("issues", []))

        if len(tickets) >= data.get("total", 0):
            break

        start_at += max_results

    return tickets


def save_tickets_backup(tickets, output_file):
    """티켓 정보를 파일로 저장합니다."""
    backup_data = {
        "timestamp": "2026-05-06",
        "total": len(tickets),
        "tickets": []
    }

    for issue in tickets:
        fields = issue["fields"]
        backup_data["tickets"].append({
            "key": issue["key"],
            "summary": fields.get("summary", ""),
            "description": fields.get("description", ""),
            "issue_type": fields["issuetype"]["name"],
            "priority": fields["priority"]["name"],
            "status": fields["status"]["name"],
            "created": fields.get("created", ""),
            "updated": fields.get("updated", ""),
            "reporter": fields.get("reporter", {}).get("displayName", "") if fields.get("reporter") else ""
        })

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)

    print(f"백업 완료: {output_file}")
    print(f"총 {len(tickets)}개 티켓 저장됨")


def main():
    parser = argparse.ArgumentParser(description="Backup Jira board tickets")
    parser.add_argument("board_id", help="Board ID (e.g., 134)")
    parser.add_argument("--output", "-o", default="data/backup/tickets_backup.json", help="Output file path")

    args = parser.parse_args()

    # 출력 디렉토리 생성
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    print(f"보드 {args.board_id}의 티켓 백업 중...")
    tickets = get_board_tickets(args.board_id)
    save_tickets_backup(tickets, args.output)


if __name__ == "__main__":
    main()
