---
name: create-bug-tasks
description: Test Execution에서 실패한 테스트 목록을 조회하여 Jira에 Bug 티켓을 생성합니다.
---

Test Execution에서 실패한 테스트 목록을 조회하여 1개의 Jira Bug 티켓으로 생성하고, 원본 Test Execution과 연결합니다.

## 입력

- Test Execution 키 (예: PLAYG-2530)

---

## 수행 단계

### 1. FAILED 테스트 목록 조회

```bash
source .env 2>/dev/null; export $(grep -v '^#' .env | xargs) 2>/dev/null
python3 AutoDevAgent/goose_assets/runner/xray_toolkit.py get_failed_tests PLAYG-2530
```

결과에서 `failed_tests` 배열을 추출합니다. `failed_count`가 0이면 "실패한 테스트가 없습니다" 메시지를 출력하고 종료합니다.

### 2. Jira Bug 티켓 생성

FAILED 테스트가 있으면 1개의 Bug 티켓을 생성합니다.

```bash
# JSON 파일 작성 후 create 명령으로 티켓 생성
cat > /tmp/bug-task.json << 'EOFJSON'
{
  "fields": {
    "project": {"key": "PLAYG"},
    "summary": "[TEST-FAIL] PLAYG-2530: N개 테스트 실패",
    "issuetype": {"name": "Bug"},
    "labels": ["test-failure"],
    "description": {
      "type": "doc",
      "version": 1,
      "content": [...]
    }
  }
}
EOFJSON
python3 AutoDevAgent/goose_assets/runner/jira_toolkit.py create /tmp/bug-task.json
```

**description 내용 (ADF 형식):**

```
## 테스트 실패 상세

| Test Case | 시나리오명 | 상태 |
|-----------|-----------|------|
| PLAYG-XXXX | 시나리오명 | FAILED |
| PLAYG-YYYY | 시나리오명 | FAILED |
| ... | ... | ... |

## Test Execution

- Test Execution: PLAYG-2530
- 총 테스트: N건
- 실패: N건

## 원인 분석

각 실패 테스트에 대해 아래 항목을 확인하세요:

- [ ] 테스트 케이스 수정 필요 (검증 기준/시나리오 불일치)
- [ ] 코드 버그 수정 필요 (기능 구현 누락/오류)

## 재현 방법

1. Vite dev server 기동 (port 5175)
2. `node tests/xray/run-all.mjs` 실행
3. FAILED 테스트 확인
```

**description은 text_to_adf 헬퍼를 사용하여 ADF(Atlassian Document Format)로 변환합니다.**
마크다운 텍스트를 먼저 작성한 후 ADF로 변환하는 접근을 사용하세요.

### 3. Test Execution과 Bug 연결

```bash
python3 AutoDevAgent/goose_assets/runner/jira_toolkit.py link PLAYG-2530 {생성된Bug키} Relates
```

### 4. Test Execution에 코멘트 등록

```bash
python3 AutoDevAgent/goose_assets/runner/jira_toolkit.py comment PLAYG-2530 "N개 실패 테스트에 대해 Bug 티켓 생성: {Bug키}"
```

---

## 주의사항

- **Bug 티켓은 1개만 생성** — 모든 FAILED 테스트를 1개 티켓에 목록화
- **코멘트는 1개만 게시** — 중간 코멘트 금지
- **파일 경로, 명령어 출력, JSON 내용을 코멘트에 포함하지 마세요**
- 모든 내용은 한국어로 작성
- FAILED 테스트가 0건이면 티켓을 생성하지 않고 종료
- description의 테이블에 모든 FAILED 테스트를 포함
