# SRS (Software Requirements Specification) 문서 생성

## 참조 소스

**오직 아래만 참조하세요:**
- 하위 System Requirement 티켓들 (Jira API로 조회)
- 같은 Gate에 속한 Intended Use 티켓

## ⚠️ 절대 규칙

- **한 번에 전체 문서를 쓰지 마세요** — 파싱 에러로 실패합니다
- **write tool, heredoc으로 긴 내용 금지** — 반드시 아래 generate_doc.py만 사용
- **섹션당 명령 1개** — 내용은 파일로 전달

## 수행 단계

1. Jira API로 현재 Document 티켓에 연결된 하위 SyRS 티켓들 전체 조회
2. 각 SyRS 티켓의 필드값 수집
3. IU 티켓 조회 (제품 컨텍스트용)

4. **문서 초기화:**
```bash
python3 goose_assets/runner/generate_doc.py init \
  --title "Software Requirements Specification" \
  --product "로컬 CBCT 웹 뷰어" \
  --project {PROJECT_KEY} --phase PA \
  --output docs/srs.md
```

5. **섹션별로 내용 작성** (각 섹션마다 2단계):
```bash
# 섹션 내용 작성 후 추가
python3 << 'PYEOF'
import pathlib
pathlib.Path('/tmp/srs_intro.txt').write_text("""
## 1. 소개

### 1.1 목적
본 문서는...

### 1.2 범위
...
""", encoding='utf-8')
PYEOF
python3 goose_assets/runner/generate_doc.py section --file /tmp/srs_intro.txt
```

6. **문서 완성:**
```bash
python3 goose_assets/runner/generate_doc.py finish \
  --ticket {TICKET_KEY} --output docs/srs.md
```

7. **Jira description 업데이트:**
```bash
python3 goose_assets/runner/jira_toolkit.py update {TICKET_KEY} temp_desc.json
```

8. Git 커밋
9. Jira 코멘트로 결과 보고

## 문서 구조

```markdown
## 1. 소개
## 2. 전체 설명
## 3. 기능적 요구사항
## 4. 비기능적 요구사항
## 5. 추적성 매트릭스
```

## 작성 규칙

- 하위 SyRS 티켓의 내용을 통합하여 SRS 형식으로 재구성
- IU 컨텍스트로 제품 전체 관점 유지
- IEC 62304에 부합하는 SRS 구조
- 한국어로 작성
