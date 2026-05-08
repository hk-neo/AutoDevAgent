# SDS (Software Detailed Design Document) 문서 생성

## 참조 소스

**오직 아래만 참조하세요:**
- SRS 문서 (GitHub docs/ 경로에서 조회)
- SAD 문서 (GitHub docs/ 경로에서 조회)

## 수행 단계

1. GitHub에서 SRS 문서 조회 (docs/srs.md)
2. GitHub에서 SAD 문서 조회 (docs/sad.md)
3. 두 문서를 바탕으로 SDS 작성

**[필수] 긴 문서는 반드시 write_file.py로 저장:**
문서 내용이 길기 때문에 절대 직접 write tool이나 heredoc을 사용하지 마세요.
반드시 아래 2단계로 저장하세요:
```bash
# 1단계: Python으로 임시 파일에 내용 작성
python3 << 'PYEOF'
import pathlib
content = """# Software Detailed Design Document
... 전체 문서 내용 ...
"""
pathlib.Path("/tmp/sds_content.md").write_text(content, encoding="utf-8")
PYEOF

# 2단계: write_file.py로 최종 위치에 저장
python3 goose_assets/runner/write_file.py docs/sds.md < /tmp/sds_content.md
```

4. **[필수] 작성한 문서 내용을 현재 Document 티켓의 description에 업데이트:**
   ```bash
   # 임시 파일에서 읽어서 description 업데이트
   python3 << 'PYEOF'
   import pathlib, json
   content = pathlib.Path("/tmp/sds_content.md").read_text(encoding="utf-8")
   pathlib.Path('temp_desc.json').write_text(json.dumps({'description': content}, ensure_ascii=False))
   PYEOF
   python3 goose_assets/runner/jira_toolkit.py update {TICKET_KEY} temp_desc.json
   ```
   이 단계를 건너뛰지 마세요. Jira 티켓에 문서가 보여야 합니다.
5. Git 커밋
6. Jira 코멘트로 결과 보고

## 문서 구조

```markdown
# Software Detailed Design Document
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
- SAD: {SAD 문서 경로}

## 2. 모듈별 상세 설계
### 2.N {모듈명}
#### 2.N.1 클래스/컴포넌트 설계
#### 2.N.2 메서드/함수 설계
#### 2.N.3 데이터 구조
#### 2.N.4 알고리즘
#### 2.N.5 에러 처리

## 3. 인터페이스 상세
### 3.N {인터페이스명}
- 입력
- 출력
- 에러 코드

## 4. 단위 테스트 계획
### 4.N {모듈명} 테스트
- 테스트 케이스
- 예상 결과

## 5. 요구사항 추적성
| SyRS ID | SAD 모듈 | SDS 컴포넌트 | 테스트 |
|---------|---------|-------------|--------|
```

## 작성 규칙

- SAD의 아키텍처를 상세 설계 수준으로 분해
- 각 모듈의 클래스/함수 수준까지 설계
- 단위 테스트 계획 포함
- IEC 62304에 부합하는 SDS 구조
- 한국어로 작성
