# SRS (Software Requirements Specification) 문서 생성

## 참조 소스

**오직 아래만 참조하세요:**
- 하위 System Requirement 티켓들 (Jira API로 조회)
- 같은 Gate에 속한 Intended Use 티켓

**절대 참조하지 마세요:**
- SAD, SDS 문서 (아직 생성 전)
- GitHub의 다른 문서

## 수행 단계

1. Jira API로 현재 Document 티켓에 연결된 하위 SyRS 티켓들 전체 조회
2. 각 SyRS 티켓의 필드값 수집
3. IU 티켓 조회 (제품 컨텍스트용)
4. 수집된 데이터로 SRS 문서 통합 작성
5. docs/srs.md 로 저장
6. Git 커밋
7. Jira 코멘트로 결과 보고

## 문서 구조

```markdown
# Software Requirements Specification
## {제품명}

### 문서 정보
- 프로젝트: {project_key}
- Phase: PA
- 버전: 1.0

---

## 1. 소개
### 1.1 목적
### 1.2 범위
### 1.3 정의, 약어, 용어

## 2. 전체 설명
### 2.1 제품 관점
### 2.2 제품 기능
### 2.3 사용자 특성
### 2.4 제약사항
### 2.5 가정 및 종속성

## 3. 기능적 요구사항
{각 Functional SyRS 티켓을 정리}
### 3.N {SyRS 제목}
- ID: {System ID}
- 설명: {description}
- 검증 기준: {Verification Criteria}

## 4. 비기능적 요구사항
### 4.1 성능 요구사항
{Performance SyRS 티켓들}
### 4.2 보안 요구사항
{Security SyRS 티켓들}
### 4.3 인터페이스 요구사항
{Interface SyRS 티켓들}

## 5. 추적성 매트릭스
| System ID | 요구사항 | 유형 | IU 연결 |
|-----------|---------|------|---------|
```

## 작성 규칙

- 하위 SyRS 티켓의 내용을 **통합**하여 SRS 형식으로 재구성
- IU 컨텍스트로 제품 전체 관점 유지
- IEC 62304에 부합하는 SRS 구조
- 각 요구사항은 추적 가능한 ID 유지
- 한국어로 작성
