---
name: create-subs
description: Gate 티켓에서 하위 티켓들을 생성합니다. Gate 타이틀에 따라 생성할 티켓 목록이 다릅니다.
---

Gate 티켓에서 하위 티켓들을 생성합니다.

## 필수 작업

1. **현재 티켓 정보 확인**
   - context.json에서 ticket_key 확인
   - Jira API로 티켓의 summary(제목) 확인

2. **Gate 타입 판별**
   - 제목에 "PA"가 포함되면 → PA Gate
   - 제목에 "EA"가 포함되면 → EA Gate

3. **Gate별 생성할 티켓 목록**

### PA Gate
| 순서 | 제목 | 이슈 타입 |
|------|------|----------|
| 1 | [Intended Use] | Document |
| 2 | [System Requirement Specification] | Document |
| 3 | [Classification] | Document |
| 4 | [SW Development Plan] | Document |
| 5 | [Risk Management Plan] | Document |
| 6 | [Security Maintenance Plan] | Document |
| 7 | [Configuration Management Plan] | Document |

### EA Gate
| 순서 | 제목 | 이슈 타입 |
|------|------|----------|
| 1 | [Risk Management Report] | Document |
| 2 | [SW Requirements Specification] | Document |
| 3 | [SW Architecture Document] | Document |
| 4 | [SW Detailed Design Document] | Document |

4. **티켓 생성**
   - jira_toolkit.py를 사용하여 각 티켓 생성
   - 생성된 티켓을 현재 Gate 티켓에 "Blocks" 링크로 연결 (Gate가 하위 티켓들을 block하는 구조)

5. **결과 보고**
   - 생성된 티켓 목록을 출력
   - 생성 성공/실패 건수

## 티켓 생성 방법

### JSON 파일 생성 후 jira_toolkit.py 사용
```bash
# 1. 필드 JSON 파일 생성
python3 -c "
import pathlib, json
fields = {
    'project': {'key': 'PROJECT_KEY'},
    'summary': '[Intended Use]',
    'issuetype': {'name': 'Document'}
}
pathlib.Path('temp_issue.json').write_text(json.dumps(fields, ensure_ascii=False))
"

# 2. 티켓 생성
python3 goose_assets/runner/jira_toolkit.py create temp_issue.json
```

### 링크 연결 (Jira API 직접 호출)
```bash
curl -s -X POST \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_URL/rest/api/3/issueLink" \
  -d '{"type": {"name": "Blocks"}, "inwardIssue": {"key": "GATE_KEY"}, "outwardIssue": {"key": "NEW_KEY"}}'
```

## 주의사항

- 프로젝트 키는 ticket_key에서 추출 (예: PLAYG-1961 → PLAYG)
- 이미 존재하는 하위 티켓은 중복 생성하지 않음
- 모든 출력은 한국어로 작성
- 제목 형식: `[문서 타입]` (예: `[Intended Use]`)
