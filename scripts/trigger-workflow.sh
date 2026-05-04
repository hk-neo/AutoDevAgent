#!/bin/bash

# GitHub Workflow 트리거 스크립트
# Jira에서 이와 비슷한 방식으로 GitHub API를 호출할 수 있음

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

# 설정 (환경 변수 또는 기본값)
GITHUB_REPO="${GITHUB_REPO:-fotogrammer/AutoDevAgent}"  # 사용자/리포지토리

# 토큰 필수 확인
if [ -z "$GITHUB_TOKEN" ]; then
  echo "Error: GITHUB_TOKEN is not set!"
  echo "Please set it in .env file or as environment variable."
  echo "Copy .env.example to .env and add your token."
  exit 1
fi

# 테스트용 페이로드
PAYLOAD=$(cat <<EOF
{
  "ticket_id": "PROJ-123",
  "command": "trace",
  "comment_id": "45678",
  "user": "developer@example.com"
}
EOF
)

# 워크플로우 트리거
echo "Triggering workflow for $GITHUB_REPO..."
echo "Payload: $PAYLOAD"

curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$GITHUB_REPO/dispatches" \
  -d "{
    \"event_type\": \"jira-command\",
    \"client_payload\": $PAYLOAD
  }"

echo -e "\n\nWorkflow triggered! Check: https://github.com/$GITHUB_REPO/actions"
