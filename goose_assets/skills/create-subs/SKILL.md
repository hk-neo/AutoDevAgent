---
name: create-subs
description: 하위 티켓들을 생성합니다. 현재 티켓 타입과 제목에 따라 생성할 티켓이 다릅니다.
---

하위 티켓들을 생성합니다. 현재 티켓의 이슈 타입과 제목에 따라 동작이 다릅니다.

## 필수 작업

1. **현재 티켓 정보 확인**
   - context.json에서 ticket_key 확인
   - Jira API로 티켓의 summary(제목)과 issuetype 확인

2. **티켓 타입에 따라 아래 지시사항을 따르세요**

---

## Case A: Gate 티켓 (issuetype = Gate)

summary에서 PA/EA 확인 후 Document 티켓들을 생성합니다.

**PA Gate** (summary에 "PA" 포함) — 7개 Document:
1. [Intended Use]
2. [System Requirement Specification]
3. [Classification]
4. [SW Development Plan]
5. [Risk Management Plan]
6. [Security Maintenance Plan]
7. [Configuration Management Plan]

**EA Gate** (summary에 "EA" 포함) — 4개 Document:
1. [Risk Management Report]
2. [SW Requirements Specification]
3. [SW Architecture Document]
4. [SW Detailed Design Document]

생성 방법: jira_toolkit.py create, "Blocks" 링크로 Gate와 연결

---

## Case B: Document [Classification] (1개만 생성)

Classification 티켓(이슈 타입: "Classification")을 **정확히 1개**만 생성합니다.
같은 Gate의 IU, SyRS 티켓을 분석하여 MDR 분류를 자동 판정합니다.

**자세한 지시사항**: `templates/classification.md` 파일을 읽으세요.

---

## Case C: Document [Risk Management Report] — Hazard 티켓 생성

ISO 14971에 따라 위해 상황(Hazard)을 식별하고, `rmr_create_hazards.py` 스크립트로 일괄 생성합니다.

### 절대 금지
- **기존 티켓/문서를 삭제하지 마세요**
- **jira_toolkit.py create를 사용하지 마세요** (스크립트가 대신 생성합니다)
- **직접 curl로 링크를 만들지 마세요** (스크립트가 대신 연결합니다)

### 수행 단계
1. 같은 Gate의 IU, SyRS 티켓 조회
2. 각 SyRS 요구사항별로 잠재적 Hazard 식별
3. **hazards.json 파일 작성** (아래 형식 참고)
4. **rmr_create_hazards.py 실행** (한 번의 명령으로 모든 Hazard 생성 + Risk Plugin + 링크 연결 완료)
5. 스크립트 출력의 코멘트용 요약을 jira_toolkit.py comment로 게시

### hazards.json 작성
아래 형식으로 파일을 작성하세요. 이것만 하면 됩니다:

```python
python3 -c "
import pathlib, json
hazards = [
    {
        'summary': '[HAZ-1.1] 영상 렌더링 오류',
        'description': '위험 원인 및 상세 설명',
        'harm': '예상되는 Harm',
        'severity': 'minor',
        'p1': 'occasional',
        'p2': 'remote',
        'source_keys': ['PLAYG-XXXX']  # 관련 SyRS/IU 티켓 키
    },
    # ... 추가 Hazard
]
pathlib.Path('hazards.json').write_text(json.dumps(hazards, ensure_ascii=False, indent=2))
"
```

### Risk 값 옵션
- **Severity**: negligible, minor, serious, critical, catastrophic
- **P1/P2**: remote, occasional, probable, frequent
- **P2는 보통 P1보다 낮거나 같음** (완화 조치 후)

### 스크립트 실행 (이 명령어 하나로 끝)
```bash
python3 goose_assets/runner/rmr_create_hazards.py hazards.json --rmr {RMR_키} --project {PROJECT_KEY}
```

스크립트가 자동으로 처리하는 작업:
- Hazard 티켓 생성 (issuetype: Hazard)
- Risk Management Plugin 활성화
- Initial/Current Risk 값 설정 (severity, P1, P2)
- Risk Source 링크 연결 (Hazard → IU/SyRS)
- Relates 링크 연결 (Hazard → RMR)
- 중복 생성 방지 (기존 Hazard 확인)

### Hazard 카테고리
영상 처리 오류, 측정 오류, 데이터 보안, UI/UX 오류, 성능 저하, 규제 미준수

**자세한 지시사항**: `templates/risk-management-report.md` 파일도 참고하세요.

---

## Case D: Document [Intended Use]

Intended Use 티켓(이슈 타입: "Intended Use")을 1개 생성합니다.
**자세한 지시사항**: `templates/intended-use.md` 파일을 읽으세요.

---

## Case E: Document [System Requirement Specification]

System Requirement 티켓(이슈 타입: "System Requirement")들을 생성합니다.
**자세한 지시사항**: `templates/system-requirement.md` 파일을 읽으세요.

---

## 공통: 티켓 생성 방법

### JSON 파일 생성 후 jira_toolkit.py 사용
```bash
python3 -c "
import pathlib, json
fields = {
    'project': {'key': '{PROJECT_KEY}'},
    'summary': '제목',
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
  -H "Accept: application/json" -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_URL/rest/api/3/issueLink" \
  -d '{"type": {"name": "Blocks"}, "inwardIssue": {"key": "GATE_KEY"}, "outwardIssue": {"key": "DOCUMENT_KEY"}}'

# Document "relates to" sub-ticket
curl -s -X POST \
  -H "Accept: application/json" -H "Content-Type: application/json" \
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
