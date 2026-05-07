---
name: create-subs
description: 하위 티켓들을 생성합니다. 현재 티켓 타입과 제목에 따라 생성할 티켓이 다릅니다.
---

하위 티켓들을 생성합니다. 현재 티켓의 이슈 타입과 제목에 따라 동작이 다릅니다.

## 1단계: 현재 티켓 정보 확인

- context.json에서 ticket_key 확인
- Jira API로 티켓의 summary(제목)과 issuetype 확인

## 2단계: 아래 분기표에 따라 해당 Case만 수행

---

## Case A: issuetype이 "Gate"인 경우

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

### 생성 방법
```bash
# JSON 파일 작성 (issuetype은 반드시 "Document")
python3 -c "
import pathlib, json
fields = {
    'project': {'key': '{PROJECT_KEY}'},
    'summary': '[문서명]',
    'issuetype': {'name': 'Document'}
}
pathlib.Path('temp_issue.json').write_text(json.dumps(fields, ensure_ascii=False))
"
python3 goose_assets/runner/jira_toolkit.py create temp_issue.json

# Blocks 링크로 Gate와 연결
curl -s -X POST \
  -H "Accept: application/json" -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_URL/rest/api/3/issueLink" \
  -d '{"type": {"name": "Blocks"}, "inwardIssue": {"key": "GATE_KEY"}, "outwardIssue": {"key": "DOCUMENT_KEY"}}'
```

---

## Case B: summary에 "[Classification]"이 포함된 Document

Classification 티켓(이슈 타입: "Classification")을 **정확히 1개**만 생성합니다.
**자세한 지시사항**: `templates/classification.md` 파일을 읽으세요.

---

## Case C: summary에 "[Risk Management Report]"이 포함된 Document

### ⚠️ 경고: 이 Case에서는 오직 Hazard 타입 티켓만 생성합니다

```
============================================================
절대로 하지 말아야 할 것:
- Document 티켓 생성 금지
- Sub-task 티켓 생성 금지
- jira_toolkit.py create 사용 금지
- Blocks 링크 사용 금지
- 기존 티켓/문서 삭제 금지
============================================================
```

ISO 14971에 따라 위해 상황(Hazard)을 식별하고, **Hazard 티켓**을 생성합니다.
**오직 risk_helper.py만 사용**하여 티켓을 생성합니다.

### 수행 단계
1. 같은 Gate의 IU, SyRS 티켓 조회
2. 기존에 연결된 Hazard 티켓이 있는지 `fetch_linked`로 확인 (있으면 건드리지 않음)
3. 각 SyRS 요구사항별로 잠재적 Hazard 식별
4. **각 Hazard를 1개씩 순차적으로 생성** (아래 명령어만 사용)
5. 올바른 추적성 링크로 연결

### Hazard 생성 — 반드시 이 명령어만 사용
```bash
# 1. Hazard JSON 작성 (issuetype이 반드시 "Hazard"여야 함)
python3 -c "
import pathlib, json
fields = {
    'project': {'key': '{PROJECT_KEY}'},
    'summary': '[HAZ-N.N] {제목}',
    'issuetype': {'name': 'Hazard'},
    'description': '{설명}',
    'customfield_10148': '{Harm}'
}
pathlib.Path('temp_hazard.json').write_text(json.dumps(fields, ensure_ascii=False))
"

# 2. risk_helper.py로 생성 + Plugin 활성화 + Risk 값 설정 (한번에)
#    jira_toolkit.py create가 아님! risk_helper.py create임!
python3 goose_assets/runner/risk_helper.py create temp_hazard.json --severity {level} --p1 {level} --p2 {level}
```

### Risk 값 옵션
- **Severity**: negligible, minor, serious, critical, catastrophic
- **P1/P2**: remote, occasional, probable, frequent
- **P2는 보통 P1보다 낮거나 같음** (완화 조치 후)

### Hazard 카테고리
영상 처리 오류, 측정 오류, 데이터 보안, UI/UX 오류, 성능 저하, 규제 미준수

### 링크 규칙
Hazard 티켓 생성 후 다음 2가지 링크를 연결합니다:

**1. Hazard → "arises from" → IU/SyRS** (위험 출처)
```bash
curl -s -X POST \
  -H "Accept: application/json" -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_URL/rest/api/3/issueLink" \
  -d '{"type": {"name": "arises from"}, "outwardIssue": {"key": "HAZARD_KEY"}, "inwardIssue": {"key": "SYRS_KEY"}}'
```
outwardIssue: Hazard (arises from 표시), inwardIssue: IU/SyRS (gives rise to 표시)

**2. Hazard → "Relates" → RMR Document** (문서 매핑)
```bash
curl -s -X POST \
  -H "Accept: application/json" -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_URL/rest/api/3/issueLink" \
  -d '{"type": {"name": "Relates"}, "inwardIssue": {"key": "HAZARD_KEY"}, "outwardIssue": {"key": "RMR_KEY"}}'
```

**자세한 지시사항**: `templates/risk-management-report.md` 파일도 참고하세요.

---

## Case D: summary에 "[Intended Use]"가 포함된 Document

Intended Use 티켓(이슈 타입: "Intended Use")을 1개 생성합니다.
**자세한 지시사항**: `templates/intended-use.md` 파일을 읽으세요.

---

## Case E: summary에 "[System Requirement Specification]"이 포함된 Document

System Requirement 티켓(이슈 타입: "System Requirement")들을 생성합니다.
**자세한 지시사항**: `templates/system-requirement.md` 파일을 읽으세요.

---

## 결과 보고

작업 완료 후 jira_toolkit.py로 현재 티켓에 결과 코멘트를 **정확히 1개만** 게시하세요.
코멘트에는 생성된 티켓 목록(키, 제목, 상태)을 표 형식으로 포함하세요.
디버그 정보, 파일 경로, 명령어 출력은 절대 포함하지 마세요.

## 주의사항

- 프로젝트 키는 ticket_key에서 추출 (예: PLAYG-1962 → PLAYG)
- 이미 존재하는 하위 티켓은 중복 생성하지 않음
- 모든 내용은 한국어로 작성
- 치과 분야 의료기기에 맞게 내용 작성
