# Risk Management Report Document 티켓 처리

Risk Management Report에서 `!create-subs`를 실행하면, IU와 SyRS를 분석하여 **Hazard 티켓들**을 생성합니다.

## 절대 금지 사항

- **기존 Hazard 티켓을 절대 삭제하지 마세요.** 이미 생성된 티켓은 그대로 두세요.
- **기존 문서(md 파일)를 삭제하지 마세요.** docs/ 폴더의 파일은 건드리지 마세요.
- **중복 생성을 방지하세요.** 생성 전에 연결된 Hazard 티켓이 이미 있는지 확인하세요.

## 수행 단계

1. **기존 Hazard 확인** — fetch_linked로 이미 연결된 Hazard 티켓이 있는지 확인. 있으면 건드리지 않음.
2. 같은 Gate의 IU 티켓과 SyRS 티켓들을 Jira API로 조회
3. IU의 사용 환경, 적응증, 경고/주의사항 분석
4. SyRS의 각 요구사항별로 잠재적 위해(Hazard) 식별
5. **각 Hazard를 1개씩 순차적으로 생성** (아래 "Hazard 티켓 생성" 섹션 참고)
6. Risk Management Report와 "Relates" 링크 연결

## Hazard 식별 방법

ISO 14971에 따라 다음 순서로 Hazard를 식별합니다:

1. **IU 분석** → 예상 사용 환경, 사용자, 적응증에서 잠재적 위해 상황 도출
2. **SyRS 분석** → 각 요구사항별로 소프트웨어 고장 시나리오 도출
3. **Hazard 카테고리별 분류:**

| 카테고리 | 예시 Hazard |
|---------|------------|
| 영상 처리 오류 | DICOM 파싱 실패, MPR 렌더링 오류, 3D 볼륨 왜곡 |
| 측정 오류 | 거리/각도 측정 부정확, Pixel Spacing 오류 |
| 데이터 보안 | 환자 정보 유출, 무단 접근 |
| UI/UX 오류 | 오입력, 혼란스러운 표시, 오류 메시지 부재 |
| 성능 저하 | 렌더링 지연, 응답 없음, 메모리 부족 |
| 규제/컴플라이언스 | 감사 추적 누락, 형상 관리 위반 |

## Hazard 티켓 생성 + Risk Plugin 활성화 + Risk 값 설정

**반드시 `risk_helper.py`를 사용하세요. 이 스크립트가 3단계를 모두 자동 처리합니다:**
1. Jira API로 Hazard 티켓 생성
2. Issue Property API로 Risk Management Plugin 패널 활성화
3. Risk Management Plugin API로 Initial/Current Risk 값 설정

**중요: Hazard 티켓을 1개씩 순차적으로 생성하세요.** 여러 개를 동시에 만들지 마세요.
각 티켓마다 JSON 작성 → risk_helper.py create → 다음 티켓 순서로 진행하세요.
API 호출 간 충분한 시간 간격이 필요합니다.

### 사용법

```bash
# Step 1: Hazard JSON 파일 작성
python3 -c "
import pathlib, json
fields = {
    'project': {'key': '{PROJECT_KEY}'},
    'summary': '[HAZ-N.N] {Hazard 제목}',
    'issuetype': {'name': 'Hazard'},
    'description': '{Hazard 상세 설명}',
    'customfield_10148': '{예상되는 Harm}'
}
pathlib.Path('temp_hazard.json').write_text(json.dumps(fields, ensure_ascii=False))
"

# Step 2: risk_helper.py로 생성 + 활성화 + Risk 값 설정 (한번에)
python3 goose_assets/runner/risk_helper.py create temp_hazard.json --severity {level} --p1 {level} --p2 {level}
```

### Risk 값 옵션

**Severity:** negligible, minor, serious, critical, catastrophic
**P1/P2:** improvable, remote, occasional, probable, frequent

### Risk 값 판정 기준

#### Severity (심각도)
- **negligible:** 불편함만, 임상적 영향 없음
- **minor:** 경미한 재처리 필요
- **serious:** 일시적 증상, 추가 진료 필요
- **critical:** 심각한 상해, 수술 필요
- **catastrophic:** 사망 또는 중대한 영구 장애

#### P1 (발생 확률 - 초기)
- **remote:** 극히 드묾
- **occasional:** 가끔 발생
- **probable:** 발생 가능성 높음
- **frequent:** 빈번히 발생

#### P2 (발생 확률 - 완화 후)
- 완화 조치(Mitigation) 적용 후의 예상 확률
- 일반적으로 P1보다 낮거나 같음

### 판정 예시 (치과 CBCT 웹 뷰어)

| Hazard | Severity | P1 | P2 | Risk Score |
|--------|----------|----|----|-----------|
| 영상 렌더링 오류 | minor | occasional | remote | 2×1=2 Low |
| 측정 오류 | serious | remote | remote | 3×1=3 Low |
| 환자 데이터 유출 | serious | remote | remote | 3×1=3 Low |
| 파일 파싱 실패 | minor | occasional | remote | 2×1=2 Low |
| 응답 없음/지연 | negligible | occasional | remote | 1×1=1 Low |

## 링크 (추적성 규칙)

각 Hazard 티켓에 대해 다음 2가지 링크를 연결합니다:

### 1. Hazard → "arises from" → IU/SyRS (위험 출처)
Hazard가 어떤 요구사항에서 도출되었는지 표시합니다.

```bash
curl -s -X POST \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_URL/rest/api/3/issueLink" \
  -d '{"type": {"name": "arises from"}, "outwardIssue": {"key": "HAZARD_KEY"}, "inwardIssue": {"key": "SYRS_KEY"}}'
```
방향: outwardIssue(Hazard)가 inwardIssue(SyRS)에서 도출됨
- Hazard 티켓에 "arises from" 표시
- SyRS 티켓에 "gives rise to" 표시

### 2. Hazard → "Relates" → RMR Document (문서 매핑)
Hazard가 어느 RMR 문서에 포함되는지 표시합니다.

```bash
curl -s -X POST \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_URL/rest/api/3/issueLink" \
  -d '{"type": {"name": "Relates"}, "inwardIssue": {"key": "HAZARD_KEY"}, "outwardIssue": {"key": "RMR_KEY"}}'
```
방향: Hazard와 RMR 문서 연결 (inwardIssue: Hazard, outwardIssue: RMR)

## 결과 보고

코멘트에 생성된 Hazard 목록을 표로 작성:

| Hazard ID | 제목 | Severity | P1→P2 | Risk Level |
|-----------|------|----------|-------|------------|
| HAZ-1.1 | 영상 렌더링 오류 | minor | 2→1 | Low |
| HAZ-1.2 | 측정 오류 | serious | 1→1 | Low |
