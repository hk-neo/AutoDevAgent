# System Requirement 상세 문서 생성

## 참조 소스

**오직 아래만 참조하세요:**
- 현재 System Requirement 티켓의 필드값
- 같은 Gate에 속한 Intended Use 티켓 (Jira API로 조회)

**절대 참조하지 마세요:**
- SRS, SAD, SDS 문서
- GitHub의 다른 문서

## 수행 단계

1. Jira API로 현재 SyRS 티켓의 모든 필드값 조회
2. Jira API로 관련 IU 티켓 조회 (Relates 링크된 티켓)
3. 필드값을 바탕으로 SyRS 상세 문서 작성
4. docs/{ticket_key}/system-requirement.md 로 저장
5. Git 커밋
6. Jira 코멘트로 결과 보고

## 문서 구조

```markdown
# System Requirement: {summary}

## 식별자
{customfield_10338 (System ID) 필드값}

## 요구사항 유형
{customfield_10108 (Requirement Type) 필드값}

## 상세 설명
{description 필드값을 확장하여 상세 작성}

## 운영환경
- OS: {customfield_10342 (OS Specifications)}
- 데이터 표준: {customfield_10345 (Data Standards)}
- 하드웨어 제약: {customfield_10340 (Hardware Constraints)}

## 사용자 제약사항
{customfield_10111 (User Constraint) 필드값}

## 성능 지표
{customfield_10344 (Performance Metrics) 필드값}

## 검증 기준
{customfield_10112 (Verification Criteria) 필드값}
```

## 작성 규칙

- IU 티켓의 컨텍스트를 참고하되, SyRS 티켓 자체의 필드값이 우선
- 요구사항은 명확하고 테스트 가능하게 작성
- "shall" 문장 형태로 각 요구사항 서술
- 한국어로 작성
