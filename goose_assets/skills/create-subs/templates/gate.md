# Gate 티켓 처리

## 1단계: Gate 타입 확인

현재 티켓의 summary를 확인하세요:
- summary에 **"PA"** 가 포함되면 → **PA Gate** (아래 PA 섹션 사용)
- summary에 **"EA"** 가 포함되면 → **EA Gate** (아래 EA 섹션 사용)

**반드시 정확한 섹션의 제목만 사용하세요. 다른 섹션의 제목을 사용하지 마세요.**

---

## PA Gate (summary에 "PA"가 포함된 경우만)

아래 7개 Document 티켓을 생성합니다:

```json
[
  {"summary": "[Intended Use]", "issuetype": "Document"},
  {"summary": "[System Requirement Specification]", "issuetype": "Document"},
  {"summary": "[Classification]", "issuetype": "Document"},
  {"summary": "[SW Development Plan]", "issuetype": "Document"},
  {"summary": "[Risk Management Plan]", "issuetype": "Document"},
  {"summary": "[Security Maintenance Plan]", "issuetype": "Document"},
  {"summary": "[Configuration Management Plan]", "issuetype": "Document"}
]
```

---

## EA Gate (summary에 "EA"가 포함된 경우만)

아래 4개 Document 티켓을 생성합니다:

```json
[
  {"summary": "[Risk Management Report]", "issuetype": "Document"},
  {"summary": "[SW Requirements Specification]", "issuetype": "Document"},
  {"summary": "[SW Architecture Document]", "issuetype": "Document"},
  {"summary": "[SW Detailed Design Document]", "issuetype": "Document"}
]
```

---

## 생성 규칙

- 빈 Document 티켓만 생성 (내용 없이 제목만)
- 각 Document에 대해 "Blocks" 링크로 Gate와 연결
  - inwardIssue: Gate 키, outwardIssue: Document 키
