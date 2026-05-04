#!/bin/bash

# GitHub Workflow 트리거 스크립트
# Jira에서 이와 비슷한 방식으로 GitHub API를 호출할 수 있음

set -e

# 설정 (실제 사용 시 환경 변수 또는 별도 설정 파일로 관리)
GITHUB_REPO="${GITHUB_REPO:-fotogrammer/AutoDevAgent}"  # 사용자/리포지토리
GITHUB_TOKEN="${GITHUB_TOKEN}"                          # GitHub Personal Access Token

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
