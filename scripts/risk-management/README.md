# Risk Management Scripts

Risk Management Plugin API를 사용하여 Jira Hazard 티켓의 Risk 값을 설정하는 스크립트들입니다.

## 사용법

### 단일 티켓의 Risk 값 설정

```bash
# Conda 환경 활성화
conda activate jira

# 스크립트 실행
python scripts/risk-management/set-risk-values.py <ticket-key>
```

### 예시

```bash
# PLAYG-1497 티켓의 Risk 값 설정
python scripts/risk-management/set-risk-values.py PLAYG-1497
```

## 스크립트 설명

### set-risk-values.py

Risk iteration의 Risk 값을 설정합니다:

- **Initial iteration**: 모든 값을 4로 설정
- **Current iteration**: 모든 값을 2로 설정

설정 항목:
- Severity (심각도)
- P1 (발생가능성 1)
- P2 (발생가능성 2)

## 설정값 매핑

### Severity Options

| 옵션 | 값 | Option ID |
|------|-----|-----------|
| negligible | 1 | 0750b204-3be7-14b2-34c9-5100846e99db |
| minor | 2 | 70ccea9f-a585-d248-dbd0-e6eefcc683e8 |
| serious | 3 | a8b765c0-2e55-f6c4-25ff-1a4513c1cfd7 |
| critical | 4 | 587d166e-890a-5123-e179-15bafbd617e1 |
| catastrophic | 5 | 981fbfd5-604d-f9b9-6765-3405a165f401 |

### Probability Options (P1)

| 옵션 | 값 | Option ID |
|------|-----|-----------|
| not selected | - | -1 |
| improvable | - | 3ac4a3b1-55ef-de93-3452-61c572a905a3 |
| remote | 1 | 2d173a68-c28f-d589-1300-bc127f962810 |
| occasional | 2 | 039596ac-784e-f0ac-50cf-d4d2cc96b096 |
| probable | 3 | 702cb81f-3bc6-d150-5cc3-daa04d3f0404 |
| frequent | 4 | 09fb301a-4448-d8aa-afd2-76d371f501f3 |

### Probability Options (P2)

| 옵션 | 값 | Option ID |
|------|-----|-----------|
| not selected | - | -1 |
| improvable | - | 7e044b34-25c4-ffae-5237-48eebb190358 |
| remote | 1 | 58257cb8-59e2-5ec7-dd1d-9e966fb13589 |
| occasional | 2 | 6cf5ebce-3b07-69b1-b093-9f0ef9def95c |
| probable | 3 | bbcbfdd1-0c02-6105-e8e4-f60ae6cacb5c |
| frequent | 4 | e35de539-93d5-f854-c6ed-50067ad8599b |

## 중요 사항

1. **API 엔드포인트**: 환경별로 다름
   - Playground: `https://306e01a8-5530-427d-b93a-f91f4898ff16.hello.atlassian-dev.net/x1/p3_h8rdLbpp1-9mjDOXQiqJ4jL4`
   - Production: 별도 확인 필요

2. **인증 토큰**: 주기적으로 갱신 필요 (Jira Automation에서 생성)

3. **설정 간 대기시간**: 각 설정 사이에 0.5초 대기

4. **Risk Set**: Initial과 Current는 별도의 Risk Set ID 사용

5. **저장 위치**: Risk Plugin DB에 저장 (Description 자동 업데이트 아님)

## Risk 계산

```
Risk Score (R) = Severity (S) × Probability (P)
```

| R 값 | 위험 등급 |
|------|---------|
| 1-3 | 낮음 (Low) |
| 4-6 | 보통 (Medium) |
| 8-12 | 높음 (High) |
| 15-25 | 매우 높음 (Very High) |

## 참고 문서

- [Risk Management Plugin API](../../docs/risk-management-plugin.md)
- [Jira Field Analysis](../../docs/jira-fields.md)
