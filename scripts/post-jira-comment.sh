#!/bin/bash
# Jira 코멘트 게시 스크립트

TICKET_KEY="$1"
COMMAND="$2"
ARGS="$3"
OUTPUT_FILE="$4"
WORKFLOW_URL="$5"

# 출력 파일에서 핵심 내용 추출 (헤더 제거)
COMMENT_BODY=$(tail -n +10 "$OUTPUT_FILE" | head -n 50 | sed 's/^/  /')

# 코멘트 작성
python3 goose_assets/runner/jira_toolkit.py comment "$TICKET_KEY" "🦆 **Goose ${COMMAND}** 실행 완료

${COMMENT_BODY}

---
*명령어: !${COMMAND} ${ARGS}*
*워크플로우: ${WORKFLOW_URL}*"
