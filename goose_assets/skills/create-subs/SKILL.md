---
name: create-subs
description: 하위 티켓들을 생성합니다. 현재 티켓 타입과 제목에 따라 생성할 티켓이 다릅니다.
---

하위 티켓들을 생성합니다. 현재 티켓의 이슈 타입과 제목에 따라 동작이 다릅니다.

## 필수 작업

1. **현재 티켓 정보 확인**
   - context.json에서 ticket_key 확인
   - Jira API로 티켓의 summary(제목)과 issuetype 확인

2. **티켓 타입에 따라 아래 지시사항을 따르세요**

---

## Case A: Gate 티켓 (issuetype = Gate)

summary에서 PA/EA 확인 후 Document 티켓들을 생성합니다.

**PA Gate** (summary에 "PA" 포함) — 7개 Document:
1. [Intended Use]
2. [System Requirement Specification]
3. [Classification]
4. [SW Development Plan]
5. [Risk Management Plan]
6. [Security Maintenance Plan]
7. [Configuration Management Plan]

**EA Gate** (summary에 "EA" 포함) — 4개 Document:
1. [Risk Management Report]
2. [SW Requirements Specification]
3. [SW Architecture Document]
4. [SW Detailed Design Document]

생성 방법: jira_toolkit.py create, "Blocks" 링크로 Gate와 연결

---

## Case B: Document [Classification] (1개만 생성)

Classification 티켓(이슈 타입: "Classification")을 **정확히 1개**만 생성합니다.
같은 Gate의 IU, SyRS 티켓을 분석하여 MDR 분류를 자동 판정합니다.

**자세한 지시사항**: `templates/classification.md` 파일을 읽으세요.

---

## Case C: Document [Risk Management Report] — Hazard 티켓 생성

ISO 14971에 따라 위해 상황(Hazard)을 식별하고, `rmr_create_hazards.py` 스크립트로 일괄 생성합니다.

### 절대 금지
- **기존 티켓/문서를 삭제하지 마세요**
- **jira_toolkit.py create를 사용하지 마세요** (스크립트가 대신 생성합니다)
- **직접 curl로 링크를 만들지 마세요** (스크립트가 대신 연결합니다)

### 수행 단계
1. 같은 Gate의 IU, SyRS 티켓 조회
2. 각 SyRS 요구사항별로 잠재적 Hazard 식별
3. **temp_hazards.json 파일 작성** (아래 형식 참고)
4. **rmr_create_hazards.py 실행** (한 번의 명령으로 모든 Hazard 생성 + Risk Plugin + 링크 연결 완료)
5. 스크립트 출력의 코멘트용 요약을 jira_toolkit.py comment로 게시

### temp_hazards.json 작성
아래 형식으로 파일을 작성하세요. 이것만 하면 됩니다:

```python
python3 -c "
import pathlib, json
hazards = [
    {
        'summary': '[HAZ-1.1] 영상 렌더링 오류',
        'description': '위험 원인 및 상세 설명',
        'harm': '예상되는 Harm',
        'severity': 'minor',
        'p1': 'occasional',
        'p2': 'remote',
        'source_keys': ['PLAYG-XXXX']  # 관련 SyRS/IU 티켓 키
    },
    # ... 추가 Hazard
]
pathlib.Path('temp_hazards.json').write_text(json.dumps(hazards, ensure_ascii=False, indent=2))
"
```

### Risk 값 옵션
- **Severity**: negligible, minor, serious, critical, catastrophic
- **P1/P2**: remote, occasional, probable, frequent
- **P2는 보통 P1보다 낮거나 같음** (완화 조치 후)

### 스크립트 실행 (이 명령어 하나로 끝)
```bash
python3 goose_assets/runner/rmr_create_hazards.py temp_hazards.json --rmr {RMR_키} --project {PROJECT_KEY}
```

스크립트가 자동으로 처리하는 작업:
- Hazard 티켓 생성 (issuetype: Hazard)
- Risk Management Plugin 활성화
- Initial/Current Risk 값 설정 (severity, P1, P2)
- Risk Source 링크 연결 (Hazard → IU/SyRS)
- Relates 링크 연결 (Hazard → RMR)
- 중복 생성 방지 (기존 Hazard 확인)

### Hazard 카테고리
영상 처리 오류, 측정 오류, 데이터 보안, UI/UX 오류, 성능 저하, 규제 미준수

**자세한 지시사항**: `templates/risk-management-report.md` 파일도 참고하세요.

---

## Case D: Document [Intended Use]

Intended Use 티켓(이슈 타입: "Intended Use")을 1개 생성합니다.
**자세한 지시사항**: `templates/intended-use.md` 파일을 읽으세요.

---

## Case E: Document [System Requirement Specification]

System Requirement 티켓(이슈 타입: "System Requirement")들을 생성합니다.
**자세한 지시사항**: `templates/system-requirement.md` 파일을 읽으세요.

---

## Case F: Document [SW Requirements Specification] — Requirement 티켓 생성

Hazard를 완화하는 SW Requirement 티켓을 생성하고, 연결된 Hazard의 Current Risk(P2) 값을 업데이트합니다.

### 절대 금지
- **jira_toolkit.py create로 직접 티켓을 만들지 마세요** (스크립트가 대신 생성합니다)
- **직접 curl로 링크를 만들지 마세요** (스크립트가 대신 연결합니다)
- **Hazard의 Initial Risk를 변경하지 마세요** (Current P2만 낮춥니다)

### 수행 단계
1. 같은 Gate의 Hazard 티켓들과 IU/SyRS 조회
2. 각 Hazard를 완화할 SW Requirement 식별
3. **temp_requirements.json 파일 작성** (아래 형식 참고)
4. **srs_create_requirements.py 실행**
5. 스크립트 출력의 코멘트용 요약을 jira_toolkit.py comment로 게시

### temp_requirements.json 작성
```python
python3 -c "
import pathlib, json
data = {
    'requirements': [
        {
            'summary': '[REQ-001] DICOM 파싱 유효성 검증',
            'description': '모든 DICOM 파일 로드 시 무결성 검증 구현...',
            'mitigates': ['PLAYG-2195'],         # 완화할 Hazard 키
            'implements': ['PLAYG-1970']          # 구현하는 System Requirement 키
        },
        # ... 추가 Requirement
    ],
    'hazard_risk_updates': {
        'PLAYG-2195': {'p2': 'remote'},  # 완화 후 Current P2
        'PLAYG-2196': {'p2': 'remote'}
    }
}
pathlib.Path('temp_requirements.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
"
```

### Risk 값 옵션
- **P2 (Current)**: remote, occasional, probable, frequent
- 완화 조치 후이므로 Initial P1보다 낮아야 함

### 스크립트 실행 (이 명령어 하나로 끝)
```bash
python3 goose_assets/runner/srs_create_requirements.py temp_requirements.json --srs {SRS_키} --project {PROJECT_KEY}
```

스크립트가 자동으로 처리하는 작업:
- Requirement 티켓 생성 (issuetype: Requirement)
- Mitigates 링크 (Requirement → Hazard): "mitigates" / "is mitigated by"
- Implements 링크 (Requirement → System Requirement): "implements" / "is implemented by"
- Relates 링크 (Requirement → SRS Document)
- Hazard Current P2 값 업데이트 (Initial Risk는 유지)

---

## Case G: Document [SW Architecture Document] — Architecture 티켓 생성

SRS의 Requirement들을 만족시키기 위한 **아키텍처 구조 결정** 티켓을 생성합니다.

**중요: 모듈 단위 분해가 아니라 아키텍처 패턴/구조 수준의 설계여야 합니다.**
- 잘못된 예: "[ARCH-001] DICOM 파서 모듈" → 이건 SDS 수준
- 올바른 예: "[ARCH-001] Rendering Pipeline Architecture" → 아키텍처 패턴/구조

### 올바른 아키텍처 티켓 예시

| 티켓 | 내용 |
|------|------|
| Frontend Architecture | 프레임워크, 컴포넌트 계층, 상태 관리 전략 |
| Rendering Pipeline Architecture | 데이터 흐름 구조 (Parse → Volume → Render), WebGL 활용 |
| Data Layer Architecture | DICOM → Volume 데이터 변환 파이프라인, 캐싱 전략 |
| Security Architecture | 로컬 전용 아키텍처, 네트워크 통신 차단 |
| UI/UX Architecture | Viewport 동기화 패턴, 이벤트 버스, 반응형 레이아웃 |

### 절대 금지
- **jira_toolkit.py create로 직접 티켓을 만들지 마세요** (스크립트가 대신 생성합니다)
- **직접 curl로 링크를 만들지 마세요** (스크립트가 대신 연결합니다)
- **요구사항별로 1:1 매핑되는 모듈을 만들지 마세요** (그건 SDS에서 합니다)

### 수행 단계
1. `docs/` 폴더의 기존 문서(IU, SyRS, SRS 등)를 읽어서 컨텍스트 파악
2. SRS의 Requirement들을 분석하여 **어떤 아키텍처 패턴/구조로 만족시킬지** 설계
3. 아키텍처 구조 결정사항을 식별 (보통 3~7개)
4. **temp_architectures.json 파일 작성** (아래 형식 참고)
5. **sad_create_architectures.py 실행**
6. 스크립트 출력의 코멘트용 요약을 jira_toolkit.py comment로 게시

### temp_architectures.json 작성
```python
python3 -c "
import pathlib, json
data = {
    'architectures': [
        {
            'summary': '[ARCH-001] Rendering Pipeline Architecture',
            'description': 'WebGL 기반 3-tier 렌더링 파이프라인 아키텍처...\n- DICOM 파싱 → Volume 데이터 구성 → GPU 렌더링\n- MPR/3D 볼륨 렌더링을 위한 셰이더 아키텍처\n- 점진적 로딩(Progressive Loading) 전략',
            'implements': ['PLAYG-2239', 'PLAYG-2240', 'PLAYG-2241']  # 관련 Requirement 키
        },
        {
            'summary': '[ARCH-002] Data Layer Architecture',
            'description': '로컬 파일 시스템 기반 데이터 아키텍처...\n- ArrayBuffer 기반 DICOM 파싱\n- Volume 데이터 캐싱 전략\n- 메모리 관리 정책',
            'implements': ['PLAYG-2239', 'PLAYG-2248']
        },
        # ... 추가 Architecture (3~7개)
    ]
}
pathlib.Path('temp_architectures.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
"
```

### 스크립트 실행 (이 명령어 하나로 끝)
```bash
python3 goose_assets/runner/sad_create_architectures.py temp_architectures.json --sad {SAD_키} --project {PROJECT_KEY}
```

스크립트가 자동으로 처리하는 작업:
- Architecture 티켓 생성 (issuetype: Architecture)
- Implements 링크 (Architecture → Requirement): "implements" / "is implemented by"
- Relates 링크 (Architecture → SAD Document)

---

## Case H: Document [SW Detailed Design Document] — Module 티켓 생성

SAD의 Architecture를 모듈/컴포넌트 수준으로 분해하여 상세 설계 Module 티켓을 생성합니다.

**아키텍처 패턴이 아니라 실제 구현 단위의 모듈이어야 합니다.**
- 올바른 예: "[MOD-001] DICOM 파일 파서", "[MOD-002] Volume 데이터 로더"
- 잘못된 예: "[MOD-001] Rendering Pipeline Architecture" → 이건 SAD 수준

### 절대 금지
- **jira_toolkit.py create로 직접 티켓을 만들지 마세요** (스크립트가 대신 생성합니다)
- **직접 curl로 링크를 만들지 마세요** (스크립트가 대신 연결합니다)

### 수행 단계
1. `docs/` 폴더의 기존 문서(SRS, SAD)를 읽어서 컨텍스트 파악
2. SAD의 Architecture 티켓들을 분석하여 **각 아키텍처를 구성하는 모듈/컴포넌트 식별**
3. 모듈 단위 분해 (보통 5~15개)
4. **temp_modules.json 파일 작성** (아래 형식 참고)
5. **sds_create_modules.py 실행**
6. 스크립트 출력의 코멘트용 요약을 jira_toolkit.py comment로 게시

### temp_modules.json 작성
```python
python3 -c "
import pathlib, json
data = {
    'modules': [
        {
            'summary': '[MOD-001] DICOM 파일 파서',
            'description': 'DICOM 파일 헤더 파싱 및 데이터 추출 모듈\n- 매직 바이트 검증\n- 필수 태그 추출 (Patient ID, Study Instance UID)\n- 전송 구문(Transfer Syntax) 처리',
            'implements': ['PLAYG-2299']  # 구현할 Architecture 키
        },
        {
            'summary': '[MOD-002] Volume 데이터 빌더',
            'description': 'DICOM 슬라이스를 3D Volume으로 구성\n- ArrayBuffer 기반 데이터 구조\n- 보간 처리 (이중선형/삼중선형)\n- 메모리 최적화',
            'implements': ['PLAYG-2299', 'PLAYG-2302']
        },
        # ... 추가 Module
    ]
}
pathlib.Path('temp_modules.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
"
```

### 스크립트 실행 (이 명령어 하나로 끝)
```bash
python3 goose_assets/runner/sds_create_modules.py temp_modules.json --sds {SDS_키} --project {PROJECT_KEY}
```

스크립트가 자동으로 처리하는 작업:
- Module 티켓 생성 (issuetype: Task)
- Implements 링크 (Module → Architecture)
- Relates 링크 (Module → SDS Document)

---

## 공통: 티켓 생성 방법

### JSON 파일 생성 후 jira_toolkit.py 사용
```bash
python3 -c "
import pathlib, json
fields = {
    'project': {'key': '{PROJECT_KEY}'},
    'summary': '제목',
    'issuetype': {'name': 'Document'}
}
pathlib.Path('temp_issue.json').write_text(json.dumps(fields, ensure_ascii=False))
"
python3 goose_assets/runner/jira_toolkit.py create temp_issue.json
```

### 링크 연결
```bash
# Gate "is blocked by" Document
curl -s -X POST \
  -H "Accept: application/json" -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_URL/rest/api/3/issueLink" \
  -d '{"type": {"name": "Blocks"}, "inwardIssue": {"key": "GATE_KEY"}, "outwardIssue": {"key": "DOCUMENT_KEY"}}'

# Document "relates to" sub-ticket
curl -s -X POST \
  -H "Accept: application/json" -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_URL/rest/api/3/issueLink" \
  -d '{"type": {"name": "Relates"}, "inwardIssue": {"key": "DOCUMENT_KEY"}, "outwardIssue": {"key": "SUB_TICKET_KEY"}}'
```

**링크 방향:**
- Gate **is blocked by** Document (inwardIssue: Gate, outwardIssue: Document)
- Document **relates to** sub-ticket (Relates는 양방향)

## 결과 보고

작업 완료 후 jira_toolkit.py로 현재 티켓에 결과 코멘트를 게시하세요.
코멘트에는 생성된 티켓 목록(키, 제목, 상태)을 표 형식으로 포함하세요.
디버그 정보는 포함하지 마세요.

## 주의사항

- 프로젝트 키는 ticket_key에서 추출 (예: PLAYG-1962 → PLAYG)
- 이미 존재하는 하위 티켓은 중복 생성하지 않음
- 모든 내용은 한국어로 작성
- 치과 분야 의료기기에 맞게 내용 작성
