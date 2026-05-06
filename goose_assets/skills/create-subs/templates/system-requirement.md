# System Requirement Specification Document 티켓 처리

command_args를 기반으로 System Requirement 티켓(이슈 타입: "System Requirement")들을 생성합니다.
command_args는 제품명이나 기능 설명입니다.

## 분할 규칙

- 제품의 기능을 분석하여 각 요구사항별로 개별 티켓 생성
- 치과 CBCT 웹 뷰어 기준으로 기능별 요구사항 도출
- 각 티켓에 적절한 필드값 자동 작성

## System Requirement 필드 목록

| 필드명 | 키 | 타입 | 설명 |
|--------|-----|------|------|
| Summary | summary | text | 요구사항 제목 |
| Phase | customfield_10382 | select | "PA" 고정 |
| Description | description | textarea | 요구사항 상세 설명 |
| Requirement Type | customfield_10108 | select | Functional, Performance, Interface, Security, Regulatory |
| System ID | customfield_10338 | text | 시스템 식별자 (예: "SyRS-001") |
| OS Specifications | customfield_10342 | select | Windows, macOS, Linux, iOS, Android, Cross-platform |
| Data Standards | customfield_10345 | multicheckboxes | HL7 FHIR, DICOM, HIPAA/GDPR, ISO 13485, IEC 62304 |
| Hardware Constraints | customfield_10340 | textarea | 하드웨어 제약사항 |
| User Constraint | customfield_10111 | textarea | 사용자 제약사항 |
| Verification Criteria | customfield_10112 | textarea | 검증 기준 |
| Performance Metrics | customfield_10344 | text | 성능 지표 |

## 생성 예시 (command_args: "로컬 CBCT 웹 뷰어")

```
생성될 티켓 목록:
1. [SyRS-001] DICOM 파일 로드 및 파싱 (Functional)
2. [SyRS-002] DICOM 메타데이터 추출 및 표시 (Functional)
3. [SyRS-003] MPR 3단면 렌더링 (Functional)
4. [SyRS-004] 슬라이스 탐색 및 제어 (Functional)
5. [SyRS-005] Window Level/Width 조절 (Functional)
6. [SyRS-006] 로컬 전용 동작 및 네트워크 차단 (Security)
7. [SyRS-007] 브라우저 호환성 (Performance)
8. [SyRS-008] 파일 크기 및 파싱 안전성 (Performance)
9. [SyRS-009] 파일 열기 인터페이스 (Interface)
10. [SyRS-010] 상태 및 진행 표시 (Functional)
```

각 티켓에는:
- summary: 요구사항 제목
- description: 요구사항 상세 설명
- Requirement Type: 요구사항 유형 자동 분류
- System ID: SyRS-NNN 형식의 식별자
- OS Specifications: "Cross-platform" (웹 뷰어이므로)
- Data Standards: ["DICOM"] (CBCT 영상이므로)
- Verification Criteria: 검증 기준
- Phase: "PA"

## 링크

- "Relates" 링크로 System Requirement Specification Document와 연결
- 관련 Intended Use 티켓과도 "Relates" 링크로 연결 (있는 경우)
