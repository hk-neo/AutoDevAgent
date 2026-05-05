#!/bin/bash

# GitHub Workflow 트리거 스크립트
# 테스트용으로 Jira 코멘트 이벤트를 시뮬레이션

set -e

# 스크립트 디렉토리 경로
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# .env 파일 로드
if [ -f "$PROJECT_ROOT/.env" ]; then
  source "$PROJECT_ROOT/.env"
  echo "Loaded .env from $PROJECT_ROOT"
else
  echo "Warning: .env file not found. Using environment variables or defaults."
fi

# 설정
GITHUB_REPO="${GITHUB_REPO:-fotogrammer/AutoDevAgent}"

# 토큰 필수 확인
if [ -z "$GITHUB_TOKEN" ]; then
  echo "Error: GITHUB_TOKEN is not set!"
  exit 1
fi

# 테스트용 설정 (인자 또는 기본값)
TICKET_KEY="${1:-PLAYG-123}"
COMMAND="${2:-help}"
COMMENT_BODY="!${COMMAND}"

# workflow_dispatch 페이로드
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$GITHUB_REPO/actions/workflows/jira-command.yml/dispatches" \
  -d "{
    \"ref\": \"main\",
    \"inputs\": {
      \"ticket_key\": \"$TICKET_KEY\",
      \"comment_body\": \"$COMMENT_BODY\"
    }
  }"

echo -e "\n\nWorkflow triggered!"
echo "  Ticket: $TICKET_KEY"
echo "  Command: !${COMMAND}"
echo "  Comment: $COMMENT_BODY"
echo "\nCheck: https://github.com/$GITHUB_REPO/actions"
