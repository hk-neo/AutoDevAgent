---
name: create-subs
description: 하위 티켓들을 생성합니다. 현재 티켓 타입과 제목에 따라 생성할 티켓이 다릅니다.
---

하위 티켓들을 생성합니다. 현재 티켓의 이슈 타입과 제목에 따라 동작이 다릅니다.

## 필수 작업

1. **현재 티켓 정보 확인**
   - context.json에서 ticket_key 확인
   - Jira API로 티켓의 summary(제목)과 issuetype 확인

2. **template 파일 선택**
   - 티켓 타입에 따라 아래 template 파일을 읽어 지시사항을 따르세요:

| 티켓 타입 | 제목 패턴 | template 파일 | 생성 수량 |
|-----------|-----------|---------------|-----------|
| Gate | PA Gate / EA Gate | `templates/gate.md` | 여러 개 |
| Document | [Intended Use] | `templates/intended-use.md` | 1개 |
| Document | [System Requirement Specification] | `templates/system-requirement.md` | 여러 개 |
| Document | [Classification] | `templates/classification.md` | **1개만** |

   template 파일 경로: `goose_assets/skills/create-subs/templates/`

3. **template에 따라 티켓 생성**

## 티켓 생성 방법

### JSON 파일 생성 후 jira_toolkit.py 사용
```bash
python3 -c "
import pathlib, json
fields = {
    'project': {'key': 'PLAYG'},
    'summary': '[Intended Use]',
    'issuetype': {'name': 'Document'}
}
pathlib.Path('temp_issue.json').write_text(json.dumps(fields, ensure_ascii=False))
"
python3 goose_assets/runner/jira_toolkit.py create temp_issue.json
```

### 링크 연결
```bash
# Gate "is blocked by" Document
curl -s -X POST \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_URL/rest/api/3/issueLink" \
  -d '{"type": {"name": "Blocks"}, "inwardIssue": {"key": "GATE_KEY"}, "outwardIssue": {"key": "DOCUMENT_KEY"}}'

# Document "relates to" sub-ticket
curl -s -X POST \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_URL/rest/api/3/issueLink" \
  -d '{"type": {"name": "Relates"}, "inwardIssue": {"key": "DOCUMENT_KEY"}, "outwardIssue": {"key": "SUB_TICKET_KEY"}}'
```

**링크 방향:**
- Gate **is blocked by** Document (inwardIssue: Gate, outwardIssue: Document)
- Document **relates to** sub-ticket (Relates는 양방향)

## 결과 보고

작업 완료 후 jira_toolkit.py로 현재 티켓에 결과 코멘트를 게시하세요.
코멘트에는 생성된 티켓 목록(키, 제목, 상태)을 표 형식으로 포함하세요.
디버그 정보는 포함하지 마세요.

## 주의사항

- 프로젝트 키는 ticket_key에서 추출 (예: PLAYG-1962 → PLAYG)
- 이미 존재하는 하위 티켓은 중복 생성하지 않음
- 모든 내용은 한국어로 작성
- 치과 분야 의료기기에 맞게 내용 작성
