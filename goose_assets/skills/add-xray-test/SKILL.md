---
name: add-xray-test
description: Xray에 새로운 Cucumber 테스트를 생성하고 테스트 스크립트를 추가합니다.
---

Xray에 새로운 Cucumber 테스트를 생성합니다. Jira Test 이슈 생성 → Cucumber 타입 변경 → Gherkin 스텝 설정 → 테스트 스크립트 추가의 전체 워크플로우를 수행합니다.

## 입력

- 테스트 키 또는 시나리오 정보
- (선택) 연결할 Test Execution 키

---

## 수행 단계

### 1. Test 이슈 생성

```bash
source .env 2>/dev/null; export $(grep -v '^#' .env | xargs) 2>/dev/null
cat > /tmp/xray-test.json << 'EOFJSON'
{
  "fields": {
    "project": {"key": "PLAYG"},
    "summary": "테스트 시나리오명",
    "issuetype": {"name": "Test"},
    "labels": ["label1", "label2"],
    "description": {
      "type": "doc",
      "version": 1,
      "content": [
        {"type": "paragraph", "content": [{"type": "text", "text": "설명"}]}
      ]
    }
  }
}
EOFJSON
python3 AutoDevAgent/goose_assets/runner/jira_toolkit.py create /tmp/xray-test.json
```

**주의:** description은 ADF(Atlassian Document Format)로 작성. `gl_FrontFacing` 등의 특수문자는 JSON 파싱 오류를 일으킬 수 있으므로 영문 설명 권장.

### 2. Issue ID 조회

Xray GraphQL API에는 Jira의 numeric issue ID가 필요합니다.

```bash
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_URL/rest/api/3/issue/{생성된키}?fields=summary" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])"
```

### 3. Cucumber 타입으로 변경

기본 생성 시 Manual 타입이므로 Cucumber로 변경합니다.

```bash
TOKEN=$(python3 AutoDevAgent/goose_assets/runner/xray_toolkit.py get_token)
curl -s -X POST "https://xray.cloud.getxray.app/api/v2/graphql" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"mutation { updateTestType(issueId: \"ISSUE_ID\", testType: { name: \"Cucumber\", kind: \"AUTOMATED\" }) }"}'
```

### 4. Gherkin 스텝 설정

```bash
curl -s -X POST "https://xray.cloud.getxray.app/api/v2/graphql" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"mutation { updateGherkinTestDefinition(issueId: \"ISSUE_ID\", gherkin: \"Given ...\\nWhen ...\\nThen ...\") }"}'
```

### 5. Test Execution에 추가 (선택)

```bash
python3 AutoDevAgent/goose_assets/runner/jira_toolkit.py link {TestExecution키} {Test키} Relates
```

### 6. 테스트 스크립트 추가

- `tests/xray/new-tests.mjs`에 테스트 함수 추가 (또는 개별 파일)
- `tests/xray/new-scenarios.json`에 시나리오 메타데이터 추가
- `tests/xray/features/N_PLAYG-XXXX.feature` Cucumber feature 파일 생성

### 7. Jira 코멘트 등록

```bash
python3 AutoDevAgent/goose_assets/runner/jira_toolkit.py comment {Test키} "Cucumber 테스트 생성 완료: {요약}"
```

---

## 주의사항

- **JSON 특수문자**: `gl_FrontFacing`, 백슬래시 등은 JSON 파싱 오류 가능. description은 영문 권장
- **issueId vs key**: Jira REST API는 key 사용, Xray GraphQL은 numeric issueId 사용
- **Cucumber 타입 변경 필수**: 기본 Manual → Cucumber 변경해야 Gherkin 설정 가능
- **Headless WebGL 제한**: 3D 렌더링 테스트는 픽셀 검증 대신 shader uniform 검증 방식 사용
- **코멘트는 1개만 게시**
- **파일 경로, 명령어 출력, JSON 내용을 코멘트에 포함하지 마세요**
- 모든 내용은 한국어로 작성
