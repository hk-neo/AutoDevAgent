# SDS (Software Detailed Design Document) 문서 생성

## 참조 소스

**오직 아래만 참조하세요:**
- SRS 문서 (GitHub docs/ 경로에서 조회)
- SAD 문서 (GitHub docs/ 경로에서 조회)

## ⚠️ 절대 규칙

- **한 번에 전체 문서를 쓰지 마세요** — 파싱 에러로 실패합니다
- **write tool, heredoc으로 긴 내용 금지** — 반드시 아래 generate_doc.py만 사용
- **섹션당 명령 1개** — 내용은 파일로 전달

## 수행 단계

1. GitHub에서 SRS 문서 조회 (docs/srs.md)
2. GitHub에서 SAD 문서 조회 (docs/sad.md)

3. **문서 초기화:**
```bash
python3 goose_assets/runner/generate_doc.py init \
  --title "Software Detailed Design Document" \
  --product "로컬 CBCT 웹 뷰어" \
  --project {PROJECT_KEY} --phase EA \
  --output docs/sds.md
```

4. **섹션별로 내용 작성** (각 섹션마다 2단계):
```bash
# 1단계: 섹션 내용을 임시 파일에 작성
python3 << 'PYEOF'
import pathlib
pathlib.Path('/tmp/sds_intro.txt').write_text("""
## 1. 소개

### 1.1 목적
본 문서는...

### 1.2 범위
...

### 1.3 참조 문서
- SRS: docs/srs.md
- SAD: docs/sad.md
""", encoding='utf-8')
PYEOF

# 2단계: generate_doc.py로 추가
python3 goose_assets/runner/generate_doc.py section --file /tmp/sds_intro.txt
```

```bash
# 다음 섹션 (2. 모듈별 상세 설계)
python3 << 'PYEOF'
import pathlib
pathlib.Path('/tmp/sds_mod1.txt').write_text("""
## 2. 모듈별 상세 설계

### 2.1 DICOM 파일 파서
#### 2.1.1 클래스 설계
...
""", encoding='utf-8')
PYEOF
python3 goose_assets/runner/generate_doc.py section --file /tmp/sds_mod1.txt
```

```bash
# 계속 섹션 추가... (한 섹션당 위 2단계 반복)
```

5. **문서 완성:**
```bash
python3 goose_assets/runner/generate_doc.py finish \
  --ticket {TICKET_KEY} --output docs/sds.md
```

6. **Jira description 업데이트** (finish 명령이 안내하는 명령어 실행):
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

## 2. 모듈별 상세 설계
### 2.N {모듈명}
#### 2.N.1 클래스/컴포넌트 설계
#### 2.N.2 메서드/함수 설계
#### 2.N.3 데이터 구조
#### 2.N.4 알고리즘
#### 2.N.5 에러 처리

## 3. 인터페이스 상세
### 3.N {인터페이스명}

## 4. 단위 테스트 계획
### 4.N {모듈명} 테스트

## 5. 요구사항 추적성
| SyRS ID | SAD 모듈 | SDS 컴포넌트 | 테스트 |
```

## 작성 규칙

- SAD의 아키텍처를 상세 설계 수준으로 분해
- 각 모듈의 클래스/함수 수준까지 설계
- 단위 테스트 계획 포함
- IEC 62304에 부합하는 SDS 구조
- 한국어로 작성
