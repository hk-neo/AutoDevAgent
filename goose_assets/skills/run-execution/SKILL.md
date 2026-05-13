---
name: run-execution
description: Test Execution에 연결된 테스트 스크립트를 실행하고 결과를 Xray에 등록합니다.
---

Test Execution에 연결된 테스트 스크립트를 실행하고 결과를 Xray에 등록합니다.

## 입력

- Test Execution 키 (예: PLAYG-2475)

---

## 수행 단계

### 1. Xray 인증 및 Test 키 조회

```bash
source .env 2>/dev/null; export $(grep -v '^#' .env | xargs) 2>/dev/null
python3 AutoDevAgent/goose_assets/runner/xray_toolkit.py get_test_keys PLAYG-2475
```

결과에서 Test 키 목록을 추출합니다.

**페이지네이션 확인**: 총 테스트 개수(total)와 조회된 키 수가 일치하는지 반드시 확인. Xray GraphQL API는 0-based 인덱싱을 사용합니다 (`start=0`부터 시작). 누락이 있으면 `xray_toolkit.py`의 `start` 초기값을 확인.

### 2. Vite Dev Server 확인

```bash
# 이미 실행 중인지 확인
curl -s http://localhost:5175 > /dev/null 2>&1 && echo "Server running" || echo "Server not running"
```

서버가 실행 중이 아니면 시작:

```bash
npx vite --port 5175 &
# 대기
```

### 3. 테스트 스크립트 실행

`tests/xray/` 디렉토리에서 각 Test 키에 해당하는 스크립트를 실행합니다.

```bash
# 각 테스트 스크립트 실행
node tests/xray/PLAYG-XXXX.mjs
```

스크립트가 없는 테스트는 SKIPPED로 처리합니다.

**실행 결과 수집:**
- 각 스크립트의 stdout에서 `PASS:` 또는 `FAIL:` 파싱
- PASSED / FAILED / SKIPPED 분류

### 4. 결과 필터링 및 Xray 등록

**중요**: 대상 Test Execution에 존재하지 않는 키가 포함되면 "Test with key XXXX not found" 에러가 발생합니다. step 1에서 조회한 키 목록에 있는 테스트만 결과에 포함하세요.

```bash
python3 AutoDevAgent/goose_assets/runner/xray_toolkit.py import_results --results-json '{
  "testExecutionKey": "PLAYG-2475",
  "tests": [
    {"testKey": "PLAYG-XXXX", "status": "PASSED", "comment": "테스트 통과"},
    {"testKey": "PLAYG-YYYY", "status": "FAILED", "comment": "에러 메시지"},
    {"testKey": "PLAYG-ZZZZ", "status": "SKIPPED", "comment": "테스트 스크립트 없음"}
  ]
}'
```

### 5. Jira 코멘트 등록

```bash
python3 AutoDevAgent/goose_assets/runner/jira_toolkit.py comment PLAYG-2475 "테스트 실행 완료: PASSED X건, FAILED X건, SKIPPED X건 (총 X건)"
```

**코멘트 형식:**

```
테스트 실행 완료
- PASSED: X건
- FAILED: X건
- SKIPPED: X건
총 X건 실행
```

---

## 주의사항

- **기존 테스트 실행 결과를 덮어쓰지 마세요** - 이미 PASSED/FAILED인 결과는 재실행하지 않습니다
- **코멘트는 1개만 게시** — 중간 코멘트 금지
- **파일 경로, 명령어 출력, JSON 내용을 코멘트에 포함하지 마세요**
- 모든 내용은 한국어로 작성
- Vite dev server가 필요하므로 실행 전 반드시 확인
- 테스트 스크립트가 없는 경우 SKIPPED로 처리하고, generate-tests 먼저 실행하라는 안내 포함
- **결과 필터링**: 대상 Test Execution에 없는 키가 포함되면 import 실패. 조회된 키만 결과에 포함
