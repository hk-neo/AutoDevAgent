#!/usr/bin/env python3
"""
Jira 보드의 모든 티켓을 삭제합니다.
"""

import argparse
import json
import os
import sys

import requests

JIRA_URL = os.getenv("JIRA_URL", "https://neobiotech.atlassian.net")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")


def get_headers():
    if not JIRA_EMAIL or not JIRA_API_TOKEN:
        raise ValueError("JIRA_EMAIL and JIRA_API_TOKEN must be set")
    return {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }


def get_auth():
    return (JIRA_EMAIL, JIRA_API_TOKEN)


def delete_ticket(ticket_key):
    """티켓을 삭제합니다."""
    url = f"{JIRA_URL}/rest/api/3/issue/{ticket_key}"
    response = requests.delete(url, headers=get_headers(), auth=get_auth())

    if response.status_code == 204:
        return True, f"삭제됨: {ticket_key}"
    elif response.status_code == 404:
        return False, f"이미 삭제됨 또는 존재하지 않음: {ticket_key}"
    else:
        return False, f"삭제 실패 ({response.status_code}): {ticket_key} - {response.text}"


def delete_board_tickets(board_id, dry_run=False):
    """보드의 모든 티켓을 삭제합니다."""
    # 보드 티켓 가져오기
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

    print(f"총 {len(tickets)}개 티켓 발견")

    if dry_run:
        print("DRY RUN - 실제 삭제하지 않음:")
        for ticket in tickets:
            print(f"  - {ticket['key']}: {ticket['fields']['summary']}")
        return

    # 티켓 삭제 (거꾸로 순회)
    success_count = 0
    fail_count = 0

    for ticket in reversed(tickets):
        success, message = delete_ticket(ticket["key"])
        if success:
            success_count += 1
            print(f"  [✓] {message}")
        else:
            fail_count += 1
            print(f"  [✗] {message}")

    print(f"\n완료: {success_count}개 삭제됨, {fail_count}개 실패")


def main():
    parser = argparse.ArgumentParser(description="Delete Jira board tickets")
    parser.add_argument("board_id", help="Board ID (e.g., 134)")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Show what would be deleted without actually deleting")

    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN 모드입니다.")
    else:
        response = input(f"정말 보드 {args.board_id}의 모든 티켓을 삭제하시겠습니까? (yes/no): ")
        if response.lower() != "yes":
            print("취소되었습니다.")
            sys.exit(0)

    delete_board_tickets(args.board_id, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
