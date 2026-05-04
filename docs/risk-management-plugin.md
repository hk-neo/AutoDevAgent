# Risk Management Plugin API

## 개요

Risk Management Plugin은 Hazard 티켓의 Risk Value (Severity, Probability 등)를 설정하기 위해 Web Request API를 사용합니다.

## API 구조

### 엔드포인트 (환경별 다름)

- **Playground**: `https://306e01a8-5530-427d-b93a-f91f4898ff16.hello.atlassian-dev.net/x1/p3_h8rdLbpp1-9mjDOXQiqJ4jL4`
- **Production**: 각 환경별로 다른 URL (Jira Automation 설정에서 확인 필요)

### 요청 형식

**Method**: `POST`

**Headers**:
```
x-trigger-authentication: [generated_token]
Content-Type: application/json
```

### 페이로드 구조

```json
{
  "issueKey": "PLAYG-1496",
  "author": "557058:f58131cb-b67d-43c7-b30d-6b58d40bd077",
  "riskModelKey": "risk-model-9dc1c741-0858-4a96-65d6-5feaf052da71",
  "riskSetId": "2f43f135-d043-84bd-4222-46ba4a309738",
  "classifierValuePayload": {
    "classifierId": "120dbe93-8a5c-89d9-398c-6fdefc8fa072",
    "optionId": "70ccea9f-a585-d248-dbd0-e6eefcc683e8"
  }
}
```

### 필드 설명

| 필드 | 설명 | 예시 |
|------|------|------|
| `issueKey` | Jira 티켓 키 | `PLAYG-1496` |
| `author` | 변경 작성자 (Account ID) | `557058:xxx` |
| `riskModelKey` | Risk 모델 식별자 | `risk-model-xxx` |
| `riskSetId` | Risk 세트 식별자 | `2f43f135-xxx` |
| `classifierId` | Risk 특성 식별자 (Severity/Probability 등) | `120dbe93-xxx` |
| `optionId` | 선택한 옵션 식별자 (Minor/Major/Critical 등) | `70ccea9f-xxx` |

## Risk 특성 (Classifier)

### Risk Model: P1-P2 ISO14971 Hazard Analysis

| 특성 | 옵션 | 값 범위 |
|------|------|--------|
| **Severity** | Negligible, Minor, Moderate, Major, Catastrophic | S=1 ~ S=5 |
| **Probability** | Remote, Low, Reasonably Probable, Probable, Frequent | P=1 ~ P=5 |
| **Detectability** | Certain, Likely, Possible, Unlikely, Improbable | D=1 ~ D=5 (선택적) |

### Risk 계산

```
Risk Score (R) = Severity (S) × Probability (P)
```

| R 값 | 위험 등급 |
|------|---------|
| 1-3 | 낮음 (Low) |
| 4-6 | 보통 (Medium) |
| 8-12 | 높음 (High) |
| 15-25 | 매우 높음 (Very High) |

## Goose 스킬에서의 활용

### 필요한 정보

1. **환경별 엔드포인트 URL**: config에 저장
2. **인증 토큰**: 환경 변수 또는 config에 저장 (주기적으로 갱신 필요)
3. **Risk Model/Set ID**: 프로젝트별로 고정된 값
4. **Classifier/Option ID**: Risk 특성별로 매핑 필요

### 설정 예시

```yaml
# config/risk-management.yml
environments:
  playground:
    endpoint: "https://306e01a8-5530-427d-b93a-f91f4898ff16.hello.atlassian-dev.net/x1/p3_h8rdLbpp1-9mjDOXQiqJ4jL4"
  production:
    endpoint: "TBD"  # Jira Automation에서 확인 필요

risk_models:
  PLAYG:
    key: "risk-model-9dc1c741-0858-4a96-65d6-5feaf052da71"
    set_id: "2f43f135-d043-84bd-4222-46ba4a309738"

classifiers:
  severity:
    id: "120dbe93-8a5c-89d9-398c-6fdefc8fa072"
    options:
      negligible: "option-id-1"
      minor: "70ccea9f-a585-d248-dbd0-e6eefcc683e8"
      moderate: "option-id-3"
      major: "option-id-4"
      catastrophic: "option-id-5"

  probability:
    id: "classifier-id-probability"
    options:
      remote: "option-id-1"
      low: "option-id-2"
      reasonably_probable: "option-id-3"
      probable: "option-id-4"
      frequent: "option-id-5"
```

## 사용 예시

### 전체 스크립트 (초기화 + 값 설정)

```python
import requests
import time

def set_risk_value(issue_key, risk_set_id, classifier_id, option_id):
    """단일 Risk 값 설정"""

    payload = {
        "issueKey": issue_key,
        "author": "557058:f58131cb-b67d-43c7-b30d-6b58d40bd077",
        "riskModelKey": risk_model_key,
        "riskSetId": risk_set_id,
        "classifierValuePayload": {
            "classifierId": classifier_id,
            "optionId": option_id
        }
    }

    headers = {
        'x-trigger-authentication': auth_token,
        'Content-Type': 'application/json'
    }

    response = requests.post(endpoint, json=payload, headers=headers)
    return response.json()
```

### 사용 가능한 스크립트

프로젝트에 포함된 스크립트를 사용하세요:

```bash
# Risk 값 설정 스크립트
python scripts/risk-management/set-risk-values.py PLAYG-1497
```

자세한 사용법은 [scripts/risk-management/README.md](../scripts/risk-management/README.md)를 참고하세요.

## 주의사항

1. **환경별 URL**: 각 환경(Playground, Production)마다 다른 엔드포인트 사용
2. **인증 토큰**: 주기적으로 갱신 필요 (Jira Automation에서 생성)
3. **ID 매핑**: Risk Model, Set, Classifier, Option ID는 프로젝트별로 다를 수 있음
4. **순서 주의**: Severity와 Probability는 별도의 API 호출로 설정해야 함
