# Gate 티켓 처리

Gate 제목으로 PA/EA 구분 후 Document 티켓들을 생성합니다.

## PA Gate
| 순서 | 제목 | 이슈 타입 |
|------|------|----------|
| 1 | [Intended Use] | Document |
| 2 | [System Requirement Specification] | Document |
| 3 | [Classification] | Document |
| 4 | [SW Development Plan] | Document |
| 5 | [Risk Management Plan] | Document |
| 6 | [Security Maintenance Plan] | Document |
| 7 | [Configuration Management Plan] | Document |

## EA Gate
| 순서 | 제목 | 이슈 타입 |
|------|------|----------|
| 1 | [Risk Management Report] | Document |
| 2 | [SW Requirements Specification] | Document |
| 3 | [SW Architecture Document] | Document |
| 4 | [SW Detailed Design Document] | Document |

## 생성 규칙

- 빈 Document 티켓만 생성 (내용 없이 제목만)
- 각 Document에 대해 "Blocks" 링크로 Gate와 연결
  - inwardIssue: Gate 키, outwardIssue: Document 키
