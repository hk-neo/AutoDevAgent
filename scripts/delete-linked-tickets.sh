#!/bin/bash
# 연결된 티켓들 삭제 스크립트

TICKET_KEY="$1"

# 연결된 티켓 목록 가져오기
LINKED_JSON=$(python3 goose_assets/runner/jira_toolkit.py fetch_linked "$TICKET_KEY" 2>/dev/null)

# 연결된 티켓 키들 추출 (jq가 없으면 grep으로)
echo "연결된 티켓 목록:"
echo "$LINKED_JSON" | grep -o '"key": "[A-Z0-9-]*"' | cut -d'"' -f4 | while read key; do
  echo "  - $key"
done

# 각 티켓 삭제 (거꾸로 순회해서 의존성 문제 방지)
echo ""
echo "티켓 삭제를 시작합니다..."
echo "$LINKED_JSON" | grep -o '"key": "[A-Z0-9-]*"' | cut -d'"' -f4 | tac | while read key; do
  if [ -n "$key" ]; then
    echo "삭제 중: $key"
    python3 goose_assets/runner/jira_toolkit.py delete "$key" 2>/dev/null || echo "  -> 삭제 실패 또는 이미 삭제됨"
  fi
done

echo ""
echo "완료되었습니다."
