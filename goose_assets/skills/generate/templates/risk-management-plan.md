# Risk Management Plan 문서 생성

## 참조 소스

**오직 아래만 참조하세요:**
- 같은 Gate의 Intended Use 티켓 (제품 컨텍스트, 적응증, 사용 환경)
- 같은 Gate의 Classification 티켓 (Safety Class, Final Class)
- 같은 Gate의 System Requirement 티켓들 (요구사항, 검증 기준)

**절대 참조하지 마세요:**
- SAD, SDS 문서 (아직 생성 전)
- 현재 작업과 무관한 외부 정보

## 수행 단계

1. Jira API로 같은 Gate에 속한 IU, Classification, SyRS 티켓 조회
2. 아래 구조에 따라 Risk Management Plan 작성
3. **[필수] 작성한 문서 내용을 현재 Document 티켓의 description에 업데이트:**
   ```bash
   python3 -c "import pathlib, json; pathlib.Path('temp_desc.json').write_text(json.dumps({'description': '문서내용'}, ensure_ascii=False))"
   python3 goose_assets/runner/jira_toolkit.py update {TICKET_KEY} temp_desc.json
   ```
   이 단계를 건너뛰지 마세요. Jira 티켓에 문서가 보여야 합니다.
4. docs/risk-management-plan.md 로도 저장
5. Git 커밋
6. Jira 코멘트로 결과 보고

## 문서 구조

```markdown
# Risk Management Plan
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
### 1.3 참조 문서 (ISO 14971, IEC 62304)

## 2. 위험 관리 정책
### 2.1 위험 허용 기준
### 2.2 위험 평가 방법론

## 3. 위험 분석
### 3.1 위험 식별 방법
### 3.2 위해 상황 식별
{IU의 Indication, Use Environment, Warnings 필드를 기반으로 위해 상황 도출}

### 3.3 위험 추정
| 위해 상황 | 위험 원인 | 가능성 | 심각도 | 위험 수준 |
|-----------|---------|--------|--------|----------|

## 4. 위험 평가
### 4.1 위험 평가 매트릭스
### 4.2 평가 결과

## 5. 위험 통제
### 5.1 통제 조치
### 5.2 잔류 위험 평가
{SyRS의 Verification Criteria를 통제 조치로 매핑}

## 6. 위험 관리 활동
### 6.1 활동 계획
### 6.2 책임자
### 6.3 일정

## 7. 위험 관리 보고
### 7.1 보고서 작성 기준
### 7.2 검토 주기
```

## 작성 규칙

- ISO 14971에 부합하는 Risk Management Plan 구조
- IU의 사용 환경, 적응증, 경고/주의사항을 위해 상황 도출에 활용
- SyRS의 검증 기준을 위험 통제 조치로 매핑
- Safety Class에 따른 위험 관리 수준 반영
- 한국어로 작성
