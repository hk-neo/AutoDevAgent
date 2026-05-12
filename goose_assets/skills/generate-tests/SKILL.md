---
name: generate-tests
description: Xray Cucumber 시나리오를 기반으로 Puppeteer 테스트 코드를 생성합니다. Test Execution 또는 Test 키를 입력받아 tests/xray/ 디렉토리에 테스트 스크립트를 생성합니다.
---

Xray에 등록된 Cucumber 테스트 시나리오를 기반으로 Puppeteer 테스트 코드를 생성합니다.

## 입력

- Test Execution 키 (예: PLAYG-2475) 또는 Test 키 (예: PLAYG-2384)
- 여러 키를 세미콜론으로 구분 가능

---

## 수행 단계

### 1. Xray 인증

```bash
source .env 2>/dev/null; export $(grep -v '^#' .env | xargs) 2>/dev/null
python3 AutoDevAgent/goose_assets/runner/xray_toolkit.py get_token
```

### 2. Cucumber Feature Export

```bash
# Test Execution 키인 경우: 먼저 Test 키 목록 조회
python3 AutoDevAgent/goose_assets/runner/xray_toolkit.py get_test_keys PLAYG-2475

# Test 키들로 feature export
python3 AutoDevAgent/goose_assets/runner/xray_toolkit.py export_cucumber "PLAYG-2384;PLAYG-2385;..." --output tests/xray
```

### 3. Feature 파일 분석

export된 `.feature` 파일을 읽고 각 시나리오의 Given/When/Then을 분석합니다.

- 각 `@TEST_PLAYG-XXXX` 태그가 붙은 Scenario가 하나의 테스트 케이스
- `@REQ_PLAYG-XXXX` 태그는 연결된 요구사항
- Given/When/Then 단계가 구체적인지 확인

### 4. Puppeteer 테스트 코드 생성

각 Test 키별로 `tests/xray/PLAYG-XXXX.mjs` 파일을 생성합니다.

**이미 존재하는 파일은 건너뛰기** (수동 수정 보호).

생성 규칙:
- `tests/xray/` 디렉토리에 저장
- `helper.mjs`의 공통 유틸리티 사용
- 각 파일은 독립적으로 실행 가능한 형태

**테스트 코드 템플릿:**

```javascript
// tests/xray/PLAYG-XXXX.mjs
// Scenario: {시나리오 이름}
// Requirement: {연결된 요구사항}

import { launchBrowser, loadDICOM, getPage } from './helper.mjs';

async function test() {
  const { browser, page } = await launchBrowser();
  try {
    // Given: {Given 내용}
    // ... 구현

    // When: {When 내용}
    // ... 구현

    // Then: {Then 내용}
    // ... 검증

    console.log(`PASS: PLAYG-XXXX - ${'{시나리오 이름}'}`);
    return { key: 'PLAYG-XXXX', status: 'PASSED' };
  } catch (e) {
    console.log(`FAIL: PLAYG-XXXX - ${e.message}`);
    return { key: 'PLAYG-XXXX', status: 'FAILED', comment: e.message };
  } finally {
    await browser.close();
  }
}

test();
```

### 5. helper.mjs 생성/업데이트

공통 유틸리티 파일. 이미 존재하면 업데이트하지 않음.

```javascript
// tests/xray/helper.mjs
import puppeteer from 'puppeteer';

export async function launchBrowser(viewport = { width: 1440, height: 900 }) {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--use-gl=angle'],
    defaultViewport: viewport,
  });
  const page = await browser.newPage();
  await page.goto('http://localhost:5175');
  return { browser, page };
}

export async function loadDICOM(page, fileCount = 200) {
  // public/dicom-test/의 파일을 HTTP fetch로 로드
  // ...
}
```

### 6. 커밋

```bash
git add tests/xray/
git commit -m "Generate Xray test scripts: {범위}"
```

---

## 주의사항

- **기존 테스트 파일을 덮어쓰지 마세요** - 수동 수정된 코드를 보호하기 위해 이미 존재하는 파일은 건너뜁니다
- **코멘트는 1개만 게시** — 중간 코멘트 금지
- **파일 경로, 명령어 출력, JSON 내용을 코멘트에 포함하지 마세요**
- 모든 내용은 한국어로 작성
- 테스트 코드는 한국어 주석과 함께 작성
- 프로젝트 키는 ticket_key에서 추출 (예: PLAYG-2384 → PLAYG)
