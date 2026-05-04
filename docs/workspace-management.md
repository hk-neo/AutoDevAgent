# Workspace Management

## 작업 공간 라이프사이클

```
┌─────────────────────────────────────────────────────────────────┐
│                    Workspace Lifecycle                          │
│                                                                 │
│  [시작]           [작업 중]              [완료/실패]             │
│    │                 │                    │                      │
│    ▼                 ▼                    ▼                      │
│  ┌──────┐         ┌──────┐            ┌──────┐                  │
│  │ 클론 │  →      │ 문서  │     →      │ 정리  │                  │
│  │      │         │ 생성  │            │      │                  │
│  │      │         │ 코드  │            │ rm -rf│                  │
│  └──────┘         │ 작성  │            │      │                  │
│  │                │      │            │      │                  │
│  │                └──────┘            └──────┘                  │
│  │                   │                                            │
│  │                   ▼                                            │
│  │               ┌──────┐                                        │
│  │               │ 푸시  │                                        │
│  │               │      │                                        │
│  │               └──────┘                                        │
│  │                                                                │
│  └────────────────────────────────────────────────────────────┘   │
│              항상 cleanup 호출 (성공/실패 무관)                      │
└─────────────────────────────────────────────────────────────────┘
```

## 작업 공간 구조

```
/workspace/
├── repos/                    # 클론된 레포지토리들
│   ├── cbct-viewer/
│   │   ├── .git/
│   │   ├── docs/
│   │   └── src/
│   └── med-records/
│       ├── .git/
│       └── docs/
├── workspaces/               # 프로젝트별 작업 공간
│   ├── cbct-proj-123/
│   │   ├── generated/        # AI 생성 문서
│   │   ├── drafts/           # 작업 중 문서
│   │   └── metadata/         # 메타데이터
│   └── med-proj-456/
│       └── ...
├── temp/                     # 임시 파일
│   ├── payloads/
│   ├── logs/
│   └── cache/
└── config/                   # 설정 파일
    ├── board-mapping.yml
    └── field-mapping.yml
```

## 정리 프로세스

### 성공 시 정리
```bash
cleanup_on_success() {
  local workspace_id=$1
  local repo_name=$2

  echo "Cleaning up workspace: $workspace_id"

  # 1. 생성된 파일들이 레포에 푸시되었는지 확인
  if git -C /workspace/repos/$repo_name push --dry-run > /dev/null 2>&1; then
    echo "Uncommitted changes found, please review before cleanup"
    return 1
  fi

  # 2. 작업 공간 삭제
  rm -rf /workspace/workspaces/$workspace_id

  # 3. 레포 삭제 (선택사항)
  rm -rf /workspace/repos/$repo_name

  # 4. 임시 파일 삭제
  rm -f /workspace/temp/payloads/${workspace_id}*.json
  rm -f /workspace/temp/logs/${workspace_id}*.log

  echo "Cleanup completed"
}
```

### 실패 시 정리
```bash
cleanup_on_error() {
  local workspace_id=$1
  local repo_name=$2

  echo "Error occurred, cleaning up workspace: $workspace_id"

  # 작업 중인 내용 저장 로그
  echo "Saving current state for debugging..."
  tar -czf /workspace/temp/failed-${workspace_id}-$(date +%s).tar.gz \
    /workspace/workspaces/$workspace_id

  # 작업 공간 삭제
  rm -rf /workspace/workspaces/$workspace_id
  rm -rf /workspace/repos/$repo_name

  echo "Cleanup completed, debug info saved"
}
```

### 항상 정리 보장
```bash
# 에러 발생 시에도 정리 실행
trap 'cleanup_on_error $WORKSPACE_ID $REPO_NAME' EXIT ERR INT TERM
```

## 디스크 사용량 관리

### 정기 정리 작업
```bash
# 오래된 작업 공간 정리 (7일 이상)
cleanup_old_workspaces() {
  find /workspace/workspaces -type d -mtime +7 -exec rm -rf {} \;
}

# 오래된 임시 파일 정리 (1일 이상)
cleanup_old_temp() {
  find /workspace/temp -type f -mtime +1 -delete
}

# 클론된 레포 정리 (30일 이상 사용 안 함)
cleanup_old_repos() {
  find /workspace/repos -type d -mtime +30 -exec rm -rf {} \;
}
```

### 모니터링
```bash
check_disk_usage() {
  local usage=$(df /workspace | tail -1 | awk '{print $5}' | sed 's/%//')
  
  if [ $usage -gt 80 ]; then
    echo "Warning: Disk usage at ${usage}%"
    # 자동 정리 트리거
    cleanup_old_workspaces
    cleanup_old_temp
  fi
}
```

## 동시 작업 처리

```python
# 작업 ID 기반 격리
class WorkspaceManager:
    def create_workspace(self, ticket_id):
        workspace_id = f"{ticket_id}-{timestamp()}"
        workspace_path = f"/workspace/workspaces/{workspace_id}"
        os.makedirs(workspace_path, exist_ok=True)
        return workspace_id

    def get_workspace(self, workspace_id):
        return f"/workspace/workspaces/{workspace_id}"
```
