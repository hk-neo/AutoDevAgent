#!/usr/bin/env python3
"""
Jira 프로젝트의 보드 목록을 가져옵니다.
"""

import os
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


# 프로젝트의 보드 찾기
project_key = "PLAYG"
url = f"{JIRA_URL}/rest/agile/1.0/board?projectKeyOrId={project_key}"

response = requests.get(url, headers=get_headers(), auth=get_auth())

if response.status_code == 200:
    boards = response.json().get("values", [])
    print("보드 목록:")
    for board in boards:
        print(f"  ID: {board['id']}, Name: {board['name']}")
else:
    print(f"Error: {response.status_code} - {response.text}")
