---
name: traceability
description: 추적성을 확인하고 관리합니다. --find-missing으로 누락된 링크 찾기, --fix로 자동 생성, --project로 전체 현황 조회를 지원합니다.
---

티켓 간 추적성 링크를 확인하고 관리합니다.

## 하위 명령어

| 명령어 | 설명 |
|--------|------|
| (기본) | 현재 티켓의 추적성 상태 확인 |
| --find-missing | 같은 Gate 내 누락된 링크 찾기 |
| --fix | 누락된 링크 자동 생성 |
| --project | 전체 프로젝트 추적성 현황 |

---

## 추적성 관계 맵 (반드시 참고)

### 링크 타입과 방향

| 출처 | 링크 타입 | 대상 | API 방향 | 설명 |
|------|-----------|------|----------|------|
| Document | Blocks | Gate | inwardIssue: Gate, outwardIssue: Document | Gate가 Document에 의해 차단됨 |
| System Requirement 티켓 | Relates | SyRS Document | 양방향 | 요구사항과 문서 연결 |
| Hazard | Risk Source | IU / System Requirement | inwardIssue: Hazard, outwardIssue: IU/SyRS | Hazard가 요구사항에서 도출됨 (inward="arises from", outward="give rise to") |
| Hazard | Relates | RMR Document | inwardIssue: Hazard, outwardIssue: RMR | Hazard와 RMR 문서 매핑 |

### PA Phase 구조

```
PA Gate
├── [Intended Use] Document              ── Blocks ──→ Gate
├── [System Requirement Specification]    ── Blocks ──→ Gate
│     └── System Requirement 티켓들      ── Relates ──→ SyRS Document
├── [Classification] Document            ── Blocks ──→ Gate
├── [SW Development Plan] Document       ── Blocks ──→ Gate
├── [Risk Management Plan] Document      ── Blocks ──→ Gate
├── [Security Maintenance Plan] Document ── Blocks ──→ Gate
└── [Configuration Management Plan]      ── Blocks ──→ Gate
```

### EA Phase 구조

```
EA Gate
├── [Risk Management Report] Document    ── Blocks ──→ Gate
│     └── Hazard 티켓들
│           ├── arises from ──→ IU / System Requirement 티켓
│           └── Relates ──→ RMR Document
├── [SW Requirements Specification]      ── Blocks ──→ Gate
├── [SW Architecture Document]           ── Blocks ──→ Gate
└── [SW Detailed Design Document]        ── Blocks ──→ Gate
```

---

## 수행 단계

### 공통 준비

1. `context.json`에서 ticket_key 확인
2. Jira API로 티켓의 summary, issuetype 확인
3. `jira_toolkit.py fetch_linked`로 현재 티켓의 기존 링크 조회

### 1. 기본: 현재 티켓 추적성 확인

현재 티켓의 모든 링크를 조회하고 상태를 보고합니다.

**수행步骤:**
1. `jira_toolkit.py fetch_linked`로 연결된 모든 티켓 조회
2. 티켓 타입별로 예상되는 링크와 실제 링크 비교
3. 결과를 표로 정리하여 코멘트 보고

**보고 형식:**

| 연결 대상 | 링크 타입 | 상태 |
|-----------|-----------|------|
| Gate 티켓 | Blocks | 연결됨 / 누락 |
| IU 티켓 | arises from | 연결됨 / 누락 |

### 2. --find-missing: 누락된 링크 찾기

같은 Gate의 모든 티켓을 조회하여 누락된 링크를 찾습니다.

**수행步骤:**
1. 현재 티켓에서 상위 Gate 찾기 (Blocks 링크 역추적)
2. Gate에 연결된 모든 Document 티켓 조회
3. 각 Document에 연결된 하위 티켓 조회
4. **각 티켓 타입별 예상 링크와 실제 링크 비교**

**티켓 타입별 예상 링크:**

| 티켓 타입 | 예상 링크 |
|-----------|-----------|
| Document (PA) | Blocks → Gate |
| System Requirement | Relates → SyRS Document |
| Hazard | arises from → IU/SyRS 티켓, Relates → RMR Document |
| Document (EA) | Blocks → Gate |

5. 누락된 링크 목록을 코멘트로 보고

**보고 형식:**

| 출처 티켓 | 대상 티켓 | 예상 링크 | 상태 |
|-----------|-----------|-----------|------|
| PLAYG-XXXX | PLAYG-YYYY | arises from | 누락 |

### 3. --fix: 누락된 링크 자동 생성

--find-missing과 동일하게 누락을 찾고, 누락된 링크를 직접 생성합니다.

**수행步骤:**
1. --find-missing 수행
2. 각 누락 항목에 대해 아래 curl로 링크 생성
3. 생성 전 `fetch_linked`로 중복 확인 (이미 존재하면 건너뛰기)
4. 생성 후 결과 코멘트 보고

**링크 생성 curl:**

```bash
# Blocks 링크 (Document → Gate)
curl -s -X POST \
  -H "Accept: application/json" -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_URL/rest/api/3/issueLink" \
  -d '{"type": {"name": "Blocks"}, "inwardIssue": {"key": "GATE_KEY"}, "outwardIssue": {"key": "DOCUMENT_KEY"}}'

# arises from 링크 (Hazard → IU/SyRS)
curl -s -X POST \
  -H "Accept: application/json" -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_URL/rest/api/3/issueLink" \
  -d '{"type": {"name": "Risk Source"}, "inwardIssue": {"key": "HAZARD_KEY"}, "outwardIssue": {"key": "SYRS_KEY"}}'

# Relates 링크 (Hazard → RMR)
curl -s -X POST \
  -H "Accept: application/json" -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_URL/rest/api/3/issueLink" \
  -d '{"type": {"name": "Relates"}, "inwardIssue": {"key": "HAZARD_KEY"}, "outwardIssue": {"key": "RMR_KEY"}}'

# Relates 링크 (System Requirement → SyRS Document)
curl -s -X POST \
  -H "Accept: application/json" -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_URL/rest/api/3/issueLink" \
  -d '{"type": {"name": "Relates"}, "inwardIssue": {"key": "SYRS_DOC_KEY"}, "outwardIssue": {"key": "SR_KEY"}}'
```

### 4. --project: 전체 프로젝트 현황

프로젝트의 모든 Gate와 그 하위 티켓의 연결 상태를 종합적으로 보고합니다.

**수행步骤:**
1. Jira API로 프로젝트의 모든 Gate 티켓 조회 (JQL: `project={PROJECT_KEY} AND issuetype=Gate`)
2. 각 Gate별로:
   - 연결된 Document 티켓 수 / 예상 수
   - 각 Document의 하위 티켓 연결 상태
   - 누락된 링크 수
3. 전체 통계: 총 티켓 수, 연결된 링크 수, 누락 수, 연결률

**보고 형식:**

| Gate | Documents | 하위 티켓 | 연결됨 | 누락 | 연결률 |
|------|-----------|-----------|--------|------|--------|
| PA Gate | 7/7 | 15 | 13 | 2 | 87% |
| EA Gate | 4/4 | 11 | 11 | 0 | 100% |

---

## 주의사항

- **기존 링크를 절대 삭제하지 마세요**
- **중복 링크 생성 금지** — 생성 전 반드시 `fetch_linked`로 확인
- **코멘트는 1개만 게시** — 중간 코멘트 금지, 디버그 정보 포함 금지
- **파일 경로, 명령어 출력, JSON 내용을 코멘트에 포함하지 마세요**
- 모든 내용은 한국어로 작성
- 프로젝트 키는 ticket_key에서 추출 (예: PLAYG-1962 → PLAYG)
