# Configuration Management Plan 문서 생성

## 참조 소스

**오직 아래만 참조하세요:**
- 같은 Gate의 Intended Use 티켓 (제품 컨텍스트)
- 같은 Gate의 System Requirement 티켓들 (전체 요구사항 범위)

**절대 참조하지 마세요:**
- SAD, SDS 문서 (아직 생성 전)
- 현재 작업과 무관한 외부 정보

## 수행 단계

1. Jira API로 같은 Gate에 속한 IU, SyRS 티켓 조회
2. 아래 구조에 따라 Configuration Management Plan 작성
3. **[필수] 작성한 문서 내용을 현재 Document 티켓의 description에 업데이트:**
   ```bash
   python3 -c "import pathlib, json; pathlib.Path('temp_desc.json').write_text(json.dumps({'description': '문서내용'}, ensure_ascii=False))"
   python3 goose_assets/runner/jira_toolkit.py update {TICKET_KEY} temp_desc.json
   ```
   이 단계를 건너뛰지 마세요. Jira 티켓에 문서가 보여야 합니다.
4. docs/{ticket_key}/configuration-management-plan.md 로도 저장
5. Git 커밋
6. Jira 코멘트로 결과 보고

## 문서 구조

```markdown
# Configuration Management Plan
## {제품명}

### 문서 정보
- 프로젝트: {project_key}
- Phase: PA
- 버전: 1.0

---

## 1. 소개
### 1.1 목적
### 1.2 범위
### 1.3 참조 문서 (IEC 62304, ISO 10007)

## 2. 형상 항목 식별
### 2.1 형상 항목 목록
| 항목 ID | 항목명 | 유형 | 담당자 |
|---------|--------|------|--------|
| CI-001 | 소스 코드 | 코드 | 개발팀 |
| CI-002 | SRS | 문서 | PM |
| CI-003 | SAD | 문서 | 아키텍트 |
| CI-004 | SDS | 문서 | 개발팀 |
| CI-005 | 테스트 케이스 | 문서 | QA |
| CI-006 | 빌드 스크립트 | 코드 | DevOps |
| CI-007 | 환경 설정 | 코드 | DevOps |

### 2.2 형상 항목 선정 기준

## 3. 형상 관리 도구 및 환경
### 3.1 버전 관리 시스템
### 3.2 이슈 추적 시스템
### 3.3 CI/CD 파이프라인

## 4. 형상 관리 활동
### 4.1 체크인/체크아웃 절차
### 4.2 브랜치 관리 전략
### 4.3 변경 요구 처리
### 4.4 형성 상태 보고

## 5. 변경 관리
### 5.1 변경 요청 절차
### 5.2 변경 영향 분석
### 5.3 변경 승인 체계
### 5.4 변경 이력 관리

## 6. 릴리스 관리
### 6.1 버전 체계 (Semantic Versioning)
### 6.2 릴리스 절차
### 6.3 릴리스 노트

## 7. 베이스라인 관리
### 7.1 베이스라인 정의
### 7.2 베이스라인 설정 시점
### 7.3 베이스라인 변경 통제
```

## 작성 규칙

- IEC 62304 Section 8에 부합하는 형상 관리 계획
- ISO 10007 참조
- SyRS의 요구사항 개수와 복잡도에 맞는 관리 수준
- GitHub, Jira를 도구로 명시 (실제 사용 환경 반영)
- 한국어로 작성
