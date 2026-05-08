# SAD (Software Architecture Document) 문서 생성

## 참조 소스

**오직 아래만 참조하세요:**
- SRS 문서 (GitHub docs/ 경로에서 조회)
- 같은 Gate에 속한 IU, SyRS 티켓들

**절대 참조하지 마세요:**
- SDS 문서 (아직 생성 전)

## 수행 단계

1. GitHub에서 SRS 문서 조회 (docs/srs.md)
2. IU, SyRS 티켓의 필드값 참조
3. SAD 문서 작성
4. **[필수] 작성한 문서 내용을 현재 Document 티켓의 description에 업데이트:**
   ```bash
   python3 -c "import pathlib, json; pathlib.Path('temp_desc.json').write_text(json.dumps({'description': '문서내용'}, ensure_ascii=False))"
   python3 goose_assets/runner/jira_toolkit.py update {TICKET_KEY} temp_desc.json
   ```
   이 단계를 건너뛰지 마세요. Jira 티켓에 문서가 보여야 합니다.
5. docs/sad.md 로도 저장
5. Git 커밋
6. Jira 코멘트로 결과 보고

## 문서 구조

```markdown
# Software Architecture Document
## {제품명}

### 문서 정보
- 프로젝트: {project_key}
- Phase: EA
- 버전: 1.0

---

## 1. 소개
### 1.1 목적
### 1.2 범위
### 1.3 참조 문서
- SRS: {SRS 문서 경로}

## 2. 아키텍처 개요
### 2.1 아키텍처 스타일
### 2.2 고수준 구조도

## 3. 모듈 설계
### 3.N {모듈명}
- 책임
- 인터페이스
- 의존성

## 4. 데이터 아키텍처
### 4.1 데이터 모델
### 4.2 데이터 흐름

## 5. 인터페이스 설계
### 5.1 외부 인터페이스
### 5.2 내부 인터페이스

## 6. 요구사항 추적성
| SyRS ID | 아키텍처 컴포넌트 |
|---------|-------------------|
```

## 작성 규칙

- SRS의 요구사항을 아키텍처 컴포넌트로 매핑
- 각 요구사항이 어느 모듈에서 구현되는지 추적 가능하게 작성
- IEC 62304에 부합하는 SAD 구조
- 한국어로 작성
