# Workflow Design

## 전체 워크플로우

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Jira      │ ───► │   GitHub    │ ───► │   Docker    │
│   Ticket    │      │   Actions   │      │   Goose     │
└─────────────┘      └─────────────┘      └─────────────┘
     │                    │                    │
     │ 1. Command         │ 2. Webhook         │ 3. Agent
     │    /@bot xxx       │    Trigger         │    Execute
     └────────────────────┴────────────────────┘
                                          │
                                          ▼
                                    ┌──────────┐
                                    │  Claude  │
                                    └──────────┘
                                          │
                                          ▼
                                    ┌──────────┐      ┌──────────┐
                                    │  Docs    │ ───► │  Git     │
                                    │  Create  │      │  Push    │
                                    └──────────┘      └──────────┘
                                          │
                                          ▼
                                    ┌──────────┐
                                    │  Jira    │
                                    │  Update  │
                                    └──────────┘
```

## 단계별 상세

### 단계 1: 초기 요청
```
사용자: "CBCT 웹 뷰어를 만들고 싶어"
    ↓
Jira 티켓 생성 (PROJ-123)
    ↓
코멘트: "@bot create intended-use"
```

### 단계 2: 문서 생성
```
Goose Agent 실행
    ↓
Claude로 Intended Use 문서 생성
    ↓
문서 내용:
  - 제품 목적
  - 의도된 사용 환경
  - 사용자 그룹
  - 적용 규정
```

### 단계 3: 리뷰 및 수정
```
문서 레포에 커밋
    ↓
Jira 티켓 업데이트 (문서 링크)
    ↓
사람 리뷰
    ↓
코멘트로 수정 요청: "의료용으로만 사용하게 제한해줘"
    ↓
Claude가 문서 수정
```

### 단계 4: 산출물 생성
```
명령: "@bot generate artifacts"
    ↓
하위 티켓 자동 생성:
  - SRS (소프트웨어 요구사항)
  - SDS (소프트웨어 설계서)
  - Architecture
  - Test Plan
    ↓
상위-하위 티켓 링크 (추적성)
```

### 단계 5: 구현 아이템 생성
```
명령: "@bot create tasks"
    ↓
SRS/SDS 기반 구현 아이템 생성:
  - TASK-001: 웹 뷰어 UI 구현
  - TASK-002: DICOM 로딩
  - TASK-003: 이미지 렌더링
    ↓
각 티켓에 해당 산출물 링크
```

## 사용자 명령어

| 명령 | 설명 | 출력 |
|------|------|------|
| `create intended-use` | Intended Use 문서 생성 | PROJ-124 (Intended Use) |
| `create srs` | SRS 문서 생성 | PROJ-125 (SRS) |
| `create sds` | SDS 문서 생성 | PROJ-126 (SDS) |
| `generate artifacts` | 모든 산출물 생성 | SRS, SDS, Architecture... |
| `create tasks` | 구현 태스크 생성 | TASK-001, TASK-002... |
| `update field X=Y` | 커스텀 필드 업데이트 | 필드 값 변경 |
| `show traceability` | 추적성 매트릭스 표시 | 티켓 관계도 |

## 진행 상황 추적

```
[완료] Intended Use (PROJ-124)
  └─ [진행 중] SRS (PROJ-125)
       ├─ [완료] 기능 요구사항 (TASK-001)
       ├─ [진행 중] 성능 요구사항 (TASK-002)
       └─ [대기] 보안 요구사항 (TASK-003)
```
