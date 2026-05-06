#!/bin/bash
# Jira 코멘트 게시 스크립트

TICKET_KEY="$1"
COMMAND="$2"
ARGS="$3"
OUTPUT_FILE="$4"
WORKFLOW_URL="$5"

# 출력 파일에서 실제 응답만 추출
# 1. 헤더 제거 (처음 6줄)
# 2. 디버그 구분선 제거
# 3. shell 명령어 출력 제거
# 4. 빈 줄 정리
COMMENT_BODY=$(cat "$OUTPUT_FILE" | \
  tail -n +7 | \
  grep -v "^  ──" | \
  grep -v "^    ▸" | \
  grep -v "^      command:" | \
  grep -v "^  ●" | \
  grep -v "^   \\\\____)" | \
  grep -v "^     L L" | \
  grep -v "goose is ready" | \
  sed '/^$/N;/^\n$/d' | \
  head -n 40)

# 코멘트 텍스트 구성
COMMENT_TEXT="🦆 **Goose ${COMMAND}** 실행 완료

${COMMENT_BODY}

---
*명령어: !${COMMAND} ${ARGS}*
*워크플로우: ${WORKFLOW_URL}*"

# 코멘트 작성
python3 goose_assets/runner/jira_toolkit.py comment "$TICKET_KEY" "$COMMENT_TEXT"
