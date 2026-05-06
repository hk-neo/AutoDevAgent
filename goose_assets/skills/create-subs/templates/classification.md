# Classification Document 티켓 처리

## MDR 분류 원칙: 제품당 1개

MDR Annex VIII에 따라 하나의 의료기기(소프트웨어)는 하나의 최종 분류를 가집니다.
여러 Rule이 동시에 적용되더라도, **가장 높은 등급**이 최종 분류가 됩니다.
IEC 62304 Software Safety Class도 소프트웨어당 1개입니다.

**→ Classification 티켓은 무조건 1개만 생성합니다.**

## 해야 할 일

1. 같은 Gate의 IU 티켓과 SyRS 티켓들을 Jira API로 조회
2. IU/SyRS 내용을 분석하여 아래 JSON의 필드값을 결정
3. jira_toolkit.py create 로 티켓 1개 생성
4. Classification Document와 "Relates" 링크 연결

## 생성할 JSON (이것 1개만 생성)

```json
{
  "fields": {
    "project": {"key": "{PROJECT_KEY}"},
    "summary": "{제품명} Classification",
    "issuetype": {"name": "Classification"},
    "customfield_10382": {"value": "PA"},
    "customfield_10346": [{"value": "Rule 11 (SW 전용 규칙)"}, {"value": "Rule 9"}],
    "customfield_10347": "{Rationale: 제품 개요, 각 Rule별 등급, 최고등급 선정 이유, Safety Class 근거를 모두 포함}",
    "customfield_10348": {"value": "Class IIa"},
    "customfield_10349": {"value": "Class B (비심각한 상해)"},
    "customfield_10163": "1.0"
  }
}
```

## 필드값 결정 기준

### Final Class (customfield_10348) — 적용 Rule 중 최고 등급
| 등급 | 기준 |
|------|------|
| Class I | 낮은 위험, 비침습적, 단순 조회 |
| Class IIa | 진단 보조, 영상 처리 |
| Class IIb | 치료 계획 직접 관여 |
| Class III | 생명 직결 |

### Software Safety Class (customfield_10349) — 최악 상해 수준
| 등급 | 기준 |
|------|------|
| Class A (안전) | 단순 조회/표시, 상해 가능성 없음 |
| Class B (비심각한 상해) | 진단 보조, 영상 처리, 최종 판단은 의사 |
| Class C (사망 또는 심각한 상해) | 치료 직접 관여, 수술 네비게이션 |

### Rules (customfield_10346) — 해당되는 모든 Rule 체크
- "Rule 11 (SW 전용 규칙)": 독립형 소프트웨어면 필수
- "Rule 9": 진단 목적
- "Rule 10": 능동 치료
- "Rule 12": 에너지 방출
- "Rule 15": 치과 분야

### Rationale (customfield_10347) — 분류 근거 서술
제품 개요 → 각 Rule별 등급 산출 → 최고등급 선정 이유 → Safety Class 판정 근거
