# SW Development Plan 문서 생성

## 참조 소스

**오직 아래만 참조하세요:**
- 같은 Gate의 Intended Use 티켓 (제품 컨텍스트)
- 같은 Gate의 Classification 티켓 (Safety Class)
- 같은 Gate의 System Requirement 티켓들 (요구사항 범위)

**절대 참조하지 마세요:**
- SAD, SDS 문서 (아직 생성 전)
- 현재 작업과 무관한 외부 정보

## 수행 단계

1. Jira API로 같은 Gate에 속한 IU, Classification, SyRS 티켓 조회
2. 아래 구조에 따라 SW Development Plan 작성
3. **현재 Document 티켓의 description을 업데이트** (jira_toolkit.py update)
4. docs/{ticket_key}/sw-dev-plan.md 로도 저장
5. Git 커밋
6. Jira 코멘트로 결과 보고

## 문서 구조

```markdown
# SW Development Plan
## {제품명}

### 문서 정보
- 프로젝트: {project_key}
- Phase: PA
- 버전: 1.0
- Software Safety Class: {Classification의 customfield_10349 값}

---

## 1. 소개
### 1.1 목적
### 1.2 범위
### 1.3 참조 문서

## 2. 조직 및 책임
### 2.1 개발 조직도
### 2.2 역할 및 책임

## 3. 개발 프로세스
### 3.1 소프트웨어 개발 라이프사이클 모델
### 3.2 단계별 산출물
### 3.3 마일스톤

## 4. 요구사항 관리
### 4.1 요구사항 수집 및 분석
### 4.2 요구사항 추적성

## 5. 설계 및 구현
### 5.1 아키텍처 설계
### 5.2 상세 설계
### 5.3 코딩 표준

## 6. 검증 및 검수
### 6.1 단위 테스트
### 6.2 통합 테스트
### 6.3 시스템 테스트

## 7. 형상 관리
### 7.1 형상 관리 도구
### 7.2 브랜치 전략
### 7.3 릴리즈 관리

## 8. 위험 관리
### 8.1 위험 식별
### 8.2 위험 완화

## 9. 품질 보증
### 9.1 코드 리뷰
### 9.2 정적 분석
### 9.3 품질 지표
```

## 작성 규칙

- IEC 62304에 부합하는 SW Development Plan 구조
- Classification의 Safety Class에 맞는 활동 수준 반영
  - Class A: 필수 활동만
  - Class B: 표준 활동
  - Class C: 강화된 활동 (독립 검증, 형식 방법 등)
- SyRS의 요구사항 범위를 반영한 개발 계획
- 한국어로 작성
- 실제 프로젝트에 적용 가능한 구체적 내용
