# Jira Field Analysis Tools

Jira 티켓의 필드 구조를 분석하고, Goose가 사용할 수 있는 매핑을 생성하는 도구들입니다.

## 도구들

### 1. analyze-ticket.py - 단일 티켓 분석

특정 Jira 티켓의 모든 필드를 분석합니다.

```bash
# 환경 변수 설정
export JIRA_URL="https://your-domain.atlassian.net"
export JIRA_EMAIL="your-email@example.com"
export JIRA_API_TOKEN="your-api-token"

# 티켓 분석
python scripts/field-analysis/analyze-ticket.py \
  "https://your-domain.atlassian.net/browse/PROJ-123"

# 결과: ticket_analysis_PROJ-123.json
```

**출력 내용:**
- 티켓 기본 정보 (ID, 타입, 상태 등)
- 모든 필드의 ID, 이름, 타입, 값
- 필드 정의 (필수 여부, 허용된 값 등)

### 2. compare-types.py - 타입별 비교

여러 타입의 티켓을 비교하여 공통 필드와 고유 필드를 식별합니다.

```bash
python scripts/field-analysis/compare-types.py \
  "https://domain.atlassian.net/browse/PROJ-123" \
  "https://domain.atlassian.net/browse/PROJ-456" \
  "https://domain.atlassian.net/browse/PROJ-789"

# 결과: type_comparison.json
```

**출력 내용:**
- 각 타입별 필드 수
- 모든 타입의 공통 필드
- 각 타입의 고유 필드
- 필드 사용 현황

### 3. generate-mapping.py - 매핑 파일 생성

분석 결과를 기반으로 Goose용 매핑 파일을 생성합니다.

```bash
python scripts/field-analysis/generate-mapping.py \
  ticket_analysis_PROJ-123.json

# 결과: field_mapping.yml
```

**출력 내용:**
- 이슈 타입 매핑
- 추적성 필드 (부모/하위 티켓)
- 상태 필드 및 옵션
- 내용 필드
- 분류되지 않은 필드 (검토 필요)

## 사용 시나리오

### 시나리오 1: 새 프로젝트 설정

```bash
# 1. 각 타입의 티켓 분석
python scripts/field-analysis/analyze-ticket.py "https://.../browse/PROJ-100"
python scripts/field-analysis/analyze-ticket.py "https://.../browse/PROJ-200"
python scripts/field-analysis/analyze-ticket.py "https://.../browse/PROJ-300"

# 2. 타입별 비교
python scripts/field-analysis/compare-types.py \
  ticket_analysis_PROJ-100.json \
  ticket_analysis_PROJ-200.json \
  ticket_analysis_PROJ-300.json

# 3. 매핑 생성
python scripts/field-analysis/generate-mapping.py ticket_analysis_PROJ-100.json
```

### 시나리오 2: 기존 매핑 업데이트

```bash
# 새로 추가된 티켓 타입 분석
python scripts/field-analysis/analyze-ticket.py "https://.../browse/NEW-TYPE-1"

# 매핑 업데이트
python scripts/field-analysis/generate-mapping.py ticket_analysis_NEW-TYPE-1.json

# 기존 매핑에 새 타입 정보 병합 (수동)
```

## 필드 분석 결과 예시

```json
{
  "analyzed_at": "2026-05-04T10:00:00",
  "ticket": {
    "id": "PROJ-123",
    "issuetype": "Intended Use",
    "summary": "CBCT 웹 뷰어"
  },
  "fields": {
    "customfield_10010": {
      "id": "customfield_10010",
      "name": "Issue Type",
      "is_custom": true,
      "type": "option",
      "value": "Intended Use"
    },
    "customfield_10020": {
      "id": "customfield_10020",
      "name": "Parent Ticket",
      "is_custom": true,
      "type": "issue",
      "value": null
    }
  },
  "field_definitions": {
    "customfield_10010": {
      "id": "customfield_10010",
      "required": true,
      "allowed_values": ["Intended Use", "SRS", "SDS", "Task"]
    }
  }
}
```

## Goose 스킬에서 활용

분석된 매핑은 Goose 스킬에서 다음과 같이 활용됩니다:

```python
# Goose 스킬 예시
from jira import JIRA

def update_issue_type(ticket_id, issue_type_name):
    # 매핑에서 필드 ID 찾기
    field_id = mapping['issue_types']['intended_use']['field_id']

    # Jira 업데이트
    jira.issue(ticket_id).update(
        fields={field_id: {"name": issue_type_name}}
    )
```

## 요구사항

```bash
pip install jira
```

## 환경 변수

| 변수 | 설명 | 예시 |
|------|------|------|
| JIRA_URL | Jira 인스턴스 URL | https://company.atlassian.net |
| JIRA_EMAIL | Jira 로그인 이메일 | user@company.com |
| JIRA_API_TOKEN | Jira API 토큰 | (Jira 설정에서 생성) |
