# Security Maintenance Plan 문서 생성

## 참조 소스

**오직 아래만 참조하세요:**
- 같은 Gate의 System Requirement 티켓들 (Security 유형 요구사항 중심)
- 같은 Gate의 Intended Use 티켓 (사용 환경, 제한사항)

**절대 참조하지 마세요:**
- SAD, SDS 문서 (아직 생성 전)
- 현재 작업과 무관한 외부 정보

## 수행 단계

1. Jira API로 같은 Gate에 속한 SyRS 티켓 중 Security 유형 조회
2. IU 티켓의 사용 환경, User Constraint 참조
3. 아래 구조에 따라 Security Maintenance Plan 작성
4. **[필수] 작성한 문서 내용을 현재 Document 티켓의 description에 업데이트:**
   ```bash
   python3 -c "import pathlib, json; pathlib.Path('temp_desc.json').write_text(json.dumps({'description': '문서내용'}, ensure_ascii=False))"
   python3 goose_assets/runner/jira_toolkit.py update {TICKET_KEY} temp_desc.json
   ```
   이 단계를 건너뛰지 마세요. Jira 티켓에 문서가 보여야 합니다.
5. docs/security-maintenance-plan.md 로도 저장
6. Git 커밋
7. Jira 코멘트로 결과 보고

## 문서 구조

```markdown
# Security Maintenance Plan
## {제품명}

### 문서 정보
- 프로젝트: {project_key}
- Phase: PA
- 버전: 1.0

---

## 1. 소개
### 1.1 목적
### 1.2 범위
### 1.3 참조 문서 (IEC 62443, IEC 81001-5-1)

## 2. 보안 위협 분석
### 2.1 자산 식별
{소프트웨어가 처리하는 데이터 자산 (환자 정보, 영상 데이터 등)}

### 2.2 위협 시나리오
{SyRS Security 요구사항을 기반으로 위협 도출}

### 2.3 취약점 분석

## 3. 보안 요구사항
### 3.1 기밀성
### 3.2 무결성
### 3.3 가용성
### 3.4 추적성 (Audit Log)
{SyRS의 Security 요구사항을 각 항목에 매핑}

## 4. 보안 통제
### 4.1 접근 통제
### 4.2 데이터 보호
### 4.3 통신 보안
### 4.4 로깅 및 모니터링

## 5. 보안 유지보수
### 5.1 취약점 모니터링
### 5.2 패치 관리
### 5.3 보안 업데이트 절차
### 5.4 사고 대응 계획

## 6. 보안 검증
### 6.1 정기 보안 점검
### 6.2 침투 테스트 계획
### 6.3 보안 검증 기준
```

## 작성 규칙

- IEC 62443, IEC 81001-5-1에 부합하는 구조
- SyRS의 Security 타입 요구사항을 보안 통제에 매핑
- IU의 Use Environment에 따른 네트워크/로컬 보안 고려
  - 로컬 전용: 물리적 보안, USB/외부매체 통제
  - 네트워크 연결: 통신 암호화, 접근 통제 강화
- 한국어로 작성
