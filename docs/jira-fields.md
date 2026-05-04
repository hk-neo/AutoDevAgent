# Jira Custom Field Management

## 문제 배경

Jira에는 프로젝트별로 많은 커스텀 필드가 존재하며, 각 필드는 `customfield_XXXXX` 형태의 ID로 식별됩니다. AI가 정확하게 필드를 업데이트하려면 이 ID들을 사전에 분석하고 매핑해야 합니다.

## Jira 필드 스캔

### 필드 스캐너
```python
# scripts/field-scanner.py
import requests
from jira import JIRA

def scan_fields(jira_url, email, api_token):
    """Jira 프로젝트의 모든 필드 스캔"""
    jira = JIRA(server=jira_url, basic_auth=(email, api_token))
    
    # 모든 필드 가져오기
    fields = jira.fields()
    
    # 커스텀 필드만 필터링
    custom_fields = [f for f in fields if f['custom']]
    
    # 분류
    result = {
        'standard': [f for f in fields if not f['custom']],
        'custom': custom_fields
    }
    
    return result
```

## 필드 매핑 구조

### 매핑 설정 파일
```yaml
# config/field-mapping.yml
project: CBCT

issue_type:
  field_id: "customfield_10010"
  name: "Issue Type"
  options:
    intended_use: "Intended Use"
    srs: "SRS"
    sds: "SDS"
    architecture: "Architecture"
    task: "Task"

traceability:
  parent_ticket:
    field_id: "customfield_10020"
    name: "Parent Ticket"
    type: "issue"
    
  sub_tickets:
    field_id: "customfield_10021"
    name: "Sub Tickets"
    type: "array_issue"
    
  linked_requirements:
    field_id: "customfield_10022"
    name: "Linked Requirements"
    type: "array_issue"

status:
  progression:
    field_id: "customfield_10030"
    name: "Progression Status"
    options:
      not_started: "Not Started"
      in_progress: "In Progress"
      review: "In Review"
      completed: "Completed"
      
  approval:
    field_id: "customfield_10031"
    name: "Approval Status"
    options:
      pending: "Pending"
      approved: "Approved"
      rejected: "Rejected"

content:
  document_content:
    field_id: "customfield_10040"
    name: "Document Content"
    type: "text_area"
    
  code_reference:
    field_id: "customfield_10041"
    name: "Code Reference"
    type: "url"
    
  test_coverage:
    field_id: "customfield_10042"
    name: "Test Coverage"
    type: "number"
```

## 필드 밸리데이터

### 업데이트 전 검증
```python
# scripts/field-validator.py
class FieldValidator:
    def __init__(self, mapping_file):
        self.mapping = self.load_mapping(mapping_file)
    
    def validate_update(self, field_name, value):
        """필드 업데이트 유효성 검사"""
        field_info = self.find_field(field_name)
        
        if not field_info:
            raise ValueError(f"Unknown field: {field_name}")
        
        if field_info['type'] == 'select':
            if value not in field_info['options']:
                raise ValueError(f"Invalid option: {value}")
        
        return True
    
    def find_field(self, field_name):
        """필드 정보 찾기"""
        for category, fields in self.mapping.items():
            if field_name in fields:
                return fields[field_name]
        return None
```

## Goose 스킬에서의 사용

### 필드 업데이트 스킬
```python
# goose/skills/traceability/update-field.py
from jira import JIRA
from field_validator import FieldValidator

def update_jira_field(ticket_id, field_name, value):
    """Jira 필드 업데이트"""
    
    # 매핑 로드
    validator = FieldValidator('config/field-mapping.yml')
    
    # 유효성 검사
    if not validator.validate_update(field_name, value):
        raise ValueError(f"Invalid field update: {field_name} = {value}")
    
    # 필드 ID 가져오기
    field_id = validator.get_field_id(field_name)
    
    # Jira 업데이트
    jira = JIRA(...)
    jira.issue(ticket_id).update(fields={field_id: value})
```

## 사용 시나리오

### 시나리오 1: 새 티켓 생성 시
```
사용자: "CBCT 프로젝트에 Intended Use 티켓 만들어줘"
    ↓
Goose Agent:
  1. field-mapping.yml 확인
  2. issue_type 필드에 "Intended Use" 설정
  3. progression_status를 "Not Started"로 초기화
  4. Jira API로 티켓 생성
```

### 시나리오 2: 문서 업데이트 시
```
사용자: "문서 내용 업데이트해줘: ..."
    ↓
Goose Agent:
  1. document_content 필드에 내용 설정
  2. code_reference 필드에 GitHub 링크 설정
  3. Jira API로 업데이트
```

### 시나리오 3: 티켓 관계 설정 시
```
사용자: "이 티켓을 SRS-123의 하위로 연결해줘"
    ↓
Goose Agent:
  1. parent_ticket 필드에 "SRS-123" 설정
  2. SRS-123의 sub_tickets에 현재 티켓 추가
  3. 양방향 업데이트
```

## 필드 스캔 도구 사용법

```bash
# 모든 필드 스캔
python scripts/field-scanner.py

# 특정 프로젝트의 필드만 스캔
python scripts/field-scanner.py --project CBCT

# 매핑 파일 자동 생성
python scripts/field-scanner.py --generate-mapping > config/field-mapping.yml
```

## 주의사항

1. **ID 고유성**: 각 Jira 인스턴스마다 커스텀 필드 ID가 다를 수 있음
2. **권한**: 필드 업데이트 시 적절한 권한 필요
3. **필수 필드**: 티켓 생성/업데이트 시 필수 필드 확인 필요
4. **동시성**: 여러 에이전트가 동시에 업데이트 시 충돌 방지 필요
