# Jira Event Architecture

## 개요

Jira 코멘트 이벤트를 처리하여 GitHub Actions 워크플로우를 트리거하고, Goose 에이전트를 통해 작업을 수행하는 구조입니다.

## 전체 아키텍처

```
┌─────────┐      ┌─────────────┐      ┌──────────┐
│  Jira   │ ───► │   Docker    │ ───► │  Goose   │
│  Ticket │      │   Server    │      │  Agent   │
└─────────┘      └─────────────┘      └──────────┘
     │                    │                    │
     │ 1. 코멘트 작성   │ 2. Webhook Trigger │ 3. 스킬 실행
     │    @!command     │    GitHub Actions   │    └─ Jira API
     └────────────────────┴────────────────────┴───────────
```

## 현재 구조 (GitHub Actions 중심)

현재는 Docker 서버가 준비되지 않았으므로 GitHub Actions 워크플로우를 중심으로 구현합니다.

```
Jira (사용자 코멘트)
    ↓
[Jira Automation/Webhook] (미구현)
    ↓
[GitHub Actions] (현재 구현)
    ├─ 코멘트 파싱
    ├─ 명령어 분리
    ├─ 명령 실행 (placeholder)
    └─ 결과 리턴
```

## GitHub Actions Workflow

### 트리거 방식

1. **workflow_dispatch** (현재 사용)
   - 테스트용으로 직접 호출
   - 개발 중에 유용

2. **repository_dispatch** (향후 확장)
   - Docker 서버에서 호출
   - Jira → Docker → GitHub Actions

3. **comment 이벤트** (목표)
   - Jira에서 코멘트 작성 시
   - Jira Automation이나 Webhook으로 중계

### 워크플로우 파일

`.github/workflows/jira-command.yml`

#### 트리거 설정

```yaml
on:
  repository_dispatch:
    types: [jira-command]
  workflow_dispatch:
    inputs:
      ticket_key: Jira 티켓 키
      comment_body: 코멘트 전체 내용
```

#### 명령 파싱

```yaml
- name: Parse command from comment
  id: parse
  run: |
    # !로 시작하는지 확인
    if echo "$COMMENT_BODY" | grep -q '^\!'; then
      COMMAND=$(echo "$COMMENT_BODY" | sed 's/^\![[:space:]]*//' | cut -d' ' -f1)
      ARGS=$(echo "$COMMENT_BODY" | sed 's/^\![[:space:]]*//' | cut -d' ' -f2-)
    else
      COMMAND="natural"
      ARGS="$COMMENT_BODY"
    fi
```

#### 명령 실행

```yaml
- name: Execute command
  id: execute
  run: |
    case "$COMMAND" in
      generate)
        echo "generate: Generating artifacts..."
        ;;
      create-subs)
        echo "create-subs: Creating sub-tickets..."
        ;;
      create-tasks)
        echo "create-tasks: Creating tasks..."
        ;;
      traceability)
        echo "traceability: Checking traceability..."
        ;;
      update)
        echo "update: Updating ticket..."
        ;;
      help)
        echo "Available commands: ..."
        ;;
      natural)
        echo "natural: Processing natural language..."
        ;;
    esac
```

## 테스트 방법

### 테스트 스크립트 사용

```bash
# 기본 사용
./scripts/trigger-workflow.sh PLAYG-123 help

# 다른 명령어
./scripts/trigger-workflow.sh PLAYG-123 generate

# 자연어 테스트
./scripts/trigger-workflow.sh PLAYG-123 "이 내용으로 수정해줘"
```

## 향후 확장

### Jira Webhook 설정 (목표)

```yaml
# Jira Automation 또는 Webhook 설정
Endpoint: <Docker Server URL>/webhook/jira
Payload:
  {
    "ticket_key": "PLAYG-123",
    "issue_id": "12345",
    "comment_id": "67890",
    "comment_body": "!generate",
    "user": "user@example.com"
  }
```

### Docker 서버 구조 (목표)

```python
# Docker 서버 웹훅 핸들러
@app.post("/webhook/jira")
def handle_jira_webhook(payload):
    # Jira 페이로드 수신
    ticket_key = payload['ticket_key']
    comment_body = payload['comment_body']

    # GitHub Actions 트리거
    trigger_github_workflow(ticket_key, comment_body)

    # 또는 직접 Goose 실행
    # result = gose.run(command, args)
```

## 이슈 및 해결 방안

### 1. Jira에서 GitHub로 직접 접근 불가

**문제**: Jira Cloud는 외부 API 호출 제한

**해결**:
- Docker 서버 중계 사용
- Jira Automation은 허용되는 API 사용
- 또는 정기 폴링 방식 (단순성을 위해 비추천)

### 2. 코멘트 내용 인코딩

**문제**: JSON 내용에 특수문자가 있을 수 있음

**해결**:
- URL 인코딩 필수
- 내용의 길이 제한 체크 필요

### 3. 동시 실행 제어

**문제**: 동시에 여러 코멘트가 올 수 있음

**해결**:
- GitHub Actions에서 자동 큐잉
- 각 작업을 독립적으로 설계

## 작업 흐름

### 1. 사용자 코멘트 작성

```
Jira 티켓에서 코멘트:
  !create-subs CBCT 웹 뷰어
```

### 2. 이벤트 전송

```
Jira → [미구현] → Docker Server
                    ↓
                GitHub Actions (현재)
```

### 3. 워크플로우 실행

```
GitHub Actions:
  1. 코멘트 파싱
  2. 명령어 식별 (!create-subs)
  3. 인자 추출 (CBCT 웹 뷰어)
  4. Goose 에이전트 호출 (또는 직접 Jira API)
```

### 4. 결과 반환

```
Goose → Jira API:
  - 하위 티켓 생성
  - 링크 설정
  - 코멘트 추가 (결과 통보)
```

## 다음 단계

1. ✅ 기본 워크플로우 구조
2. ⏳ Goose 에이전트 통합
3. ⏳ Jira Webhook 설정
4. ⏳ Docker 서버 구현
5. ⏳ 실제 명령 로직 구현
