# SAD (Software Architecture Document) 문서 생성

## 참조 소스

**오직 아래만 참조하세요:**
- SRS 문서 (GitHub docs/ 경로에서 조회)
- 같은 Gate에 속한 IU, SyRS 티켓들

## ⚠️ 절대 규칙

- **한 번에 전체 문서를 쓰지 마세요** — 파싱 에러로 실패합니다
- **write tool, heredoc으로 긴 내용 금지** — 반드시 아래 generate_doc.py만 사용
- **섹션당 명령 1개** — 내용은 파일로 전달

## 수행 단계

1. GitHub에서 SRS 문서 조회 (docs/srs.md)
2. IU, SyRS 티켓의 필드값 참조

3. **문서 초기화:**
```bash
python3 goose_assets/runner/generate_doc.py init \
  --title "Software Architecture Document" \
  --product "로컬 CBCT 웹 뷰어" \
  --project {PROJECT_KEY} --phase EA \
  --output docs/sad.md
```

4. **섹션별로 내용 작성** (각 섹션마다 2단계):
```bash
# 섹션 내용 작성 후 추가
python3 << 'PYEOF'
import pathlib
pathlib.Path('/tmp/sad_intro.txt').write_text("""
## 1. 소개

### 1.1 목적
본 문서는...

### 1.2 범위
...

### 1.3 참조 문서
- SRS: docs/srs.md
""", encoding='utf-8')
PYEOF
python3 goose_assets/runner/generate_doc.py section --file /tmp/sad_intro.txt
```

5. **문서 완성:**
```bash
python3 goose_assets/runner/generate_doc.py finish \
  --ticket {TICKET_KEY} --output docs/sad.md
```

6. **Jira description 업데이트:**
```bash
python3 goose_assets/runner/jira_toolkit.py update {TICKET_KEY} temp_desc.json
```

7. Git 커밋
8. Jira 코멘트로 결과 보고

## 문서 구조

```markdown
## 1. 소개
### 1.1 목적
### 1.2 범위
### 1.3 참조 문서

## 2. 아키텍처 개요
### 2.1 아키텍처 스타일
### 2.2 고수준 구조도

## 3. 모듈 설계
### 3.N {모듈명}

## 4. 데이터 아키텍처
## 5. 인터페이스 설계
## 6. 요구사항 추적성
```

## 작성 규칙

- SRS의 요구사항을 아키텍처 컴포넌트로 매핑
- IEC 62304에 부합하는 SAD 구조
- 한국어로 작성
