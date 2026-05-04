# System Architecture

## 멀티-보드/멀티-레포 지원

```
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Server (Goose)                        │
│                                                                 │
│  [Jira 티켓 ID 식별] → [레포 매핑 조회] → [레포 클론]            │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │ Jira Board A│ →  │ Repo Alpha  │    │ Workspace 1 │          │
│  │ (CBCT)      │    │ (cbct-viewer)│   │ /ws/cbct/   │          │
│  └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │ Jira Board B│ →  │ Repo Beta   │    │ Workspace 2 │          │
│  │ (MedRecord) │    │ (med-records)│   │ /ws/med/    │          │
│  └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │ Jira Board C│ →  │ Repo Gamma  │    │ Workspace 3 │          │
│  │ (PACS)      │    │ (pacs-server) │   │ /ws/pacs/   │          │
│  └─────────────┘    └─────────────┘    └─────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## 컴포넌트 구조

```
AutoDevAgent/
├── .github/workflows/
│   └── jira-command.yml      # GitHub Actions 워크플로우
├── scripts/
│   ├── trigger-workflow.sh   # 테스트용 트리거
│   └── field-scanner.py      # Jira 필드 스캐너
├── goose/
│   ├── skills/               # Goose 스킬들
│   │   ├── traceability/     # 추적성 관리 스킬
│   │   ├── documentation/    # 문서 생성 스킬
│   │   └── implementation/   # 구현 관리 스킬
│   └── config/               # Goose 설정
├── config/
│   ├── board-mapping.yml     # Jira-GitHub 매핑
│   └── field-mapping.yml     # 커스텀 필드 매핑
├── docs/                     # 문서
└── .env                      # 환경 변수
```

## 레포 매핑 설정

```yaml
# config/board-mapping.yml
boards:
  - jira_project: "CBCT"
    github_repo: "hk-neo/cbct-viewer"
    github_token: "${GITHUB_TOKEN_CBCT}"
    branch_prefix: "feature/"
    workspace_id: "cbct"
    issue_types:
      intended_use: "Intended Use"
      srs: "SRS"
      sds: "SDS"
      architecture: "Architecture"
      task: "Task"

  - jira_project: "MED"
    github_repo: "hk-neo/med-records"
    github_token: "${GITHUB_TOKEN_MED}"
    branch_prefix: "med/"
    workspace_id: "med"
    issue_types:
      intended_use: "Intended Use"
      srs: "SRS"
      sds: "SDS"
      task: "Task"
```

## 통신 흐름

### 1. Jira → GitHub
```
Jira Automation/Webhook
    ↓
GitHub API (repository_dispatch)
    ↓
GitHub Actions Workflow
```

### 2. GitHub → Docker
```
GitHub Actions
    ↓
REST API Call to Docker Server
    ↓
Goose Agent Trigger
```

### 3. Docker → Jira
```
Goose Agent
    ↓
Jira REST API
    ↓
Ticket/Field Update
```

### 4. Docker → GitHub
```
Goose Agent
    ↓
Git Push
    ↓
Repository Update
```

## 확장성 고려사항

1. **새로운 보드 추가**: `board-mapping.yml`에 엔트리만 추가
2. **새로운 스킬 추가**: `goose/skills/`에 새 스킬 디렉토리
3. **새로운 명령 추가**: 스킬 내에서 새 명령 핸들러 구현
