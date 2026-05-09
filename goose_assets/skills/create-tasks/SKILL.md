---
name: create-tasks
description: SDS Detailed Design 티켓들을 기반으로 Bottom-Up 순서로 구현 Task 티켓을 생성합니다.
---

SDS의 Detailed Design 티켓들을 기반으로 **Bottom-Up** 순서로 구현 Task 티켓을 생성합니다.

**이 스크립트는 sds_create_tasks.py만 사용합니다. 다른 방법은 사용하지 마세요.**

## ⚠️ 반드시 지켜야 할 규칙

1. **jira_toolkit.py create 절대 사용 금지** — 티켓 생성은 스크립트가 합니다
2. **직접 curl로 링크 금지** — 링크도 스크립트가 합니다
3. **반드시 sds_create_tasks.py만 사용**

## Bottom-Up 원칙

의존성이 없는 것부터 먼저 만듭니다. 하위 모듈이 완성되어야 상위 모듈을 조립할 수 있습니다.

```
Phase 1: Foundation
  → 공유 타입, 인터페이스, 상수, UI 컴포넌트 스펙

Phase 2: Data Layer
  → DICOM 파서, Volume 빌더, 메모리 관리

Phase 3: Rendering Engine
  → MPR 렌더러, 3D 볼륨 렌더러, 카메라, Windowing

Phase 4: Features
  → 측정 도구, ROI, 좌표 변환, 뷰포트 동기화

Phase 5: UI Shell & Integration
  → 앱 셸, 컴포넌트 조립, 상태 관리, 반응형 레이아웃

Phase 6: Security & Polish
  → 보안 검증, 성능 최적화, 브라우저 호환성
```

## 필수 작업

### 1. 현재 티켓 정보 확인
- context.json에서 ticket_key 확인
- Jira API로 티켓의 summary, issuetype 확인

### 2. 컨텍스트 수집
- `docs/` 폴더에서 SRS, SAD, SDS 문서 읽기
- Jira API로 **연결된 Detailed Design 티켓들 전체 조회** (Relates 링크)
- 각 Detailed Design 티켓의 description까지 상세 조회
- 연결된 Architecture 티켓들 조회
- 연결된 Requirement 티켓들 조회

### 3. Task 분해

각 Detailed Design 티켓의 클래스/모듈을 실제 구현 단위의 Task로 분해합니다.

**Task 크기 가이드:**
- 한 Task = 1~3개 클래스 또는 1개 독립 기능
- 한 Task당 예상 2~8시간 작업량
- 너무 크면 분할, 너무 작으면 병합

**Task description에 포함할 내용:**
```
## 구현 대상
- 구현할 클래스/함수 목록

## 상세 설계
- 클래스별 필드, 메서드 시그니처
- 알고리즘 의사코드

## 의존성
- 선행 Task (blocks)
- 참조할 인터페이스/타입

## 검증 기준
- 단위 테스트 케이스
- 완료 조건 (Definition of Done)
```

### 4. 의존성 그래프 생성

Task 간 의존성을 분석하여 Blocks 링크로 연결:
- `create_link('Blocks', 후행_Task, 선행_Task)`
- 후행_Task는 선행_Task가 완료될 때까지 대기
- 순환 의존성 감지 시 경고

### 5. temp_tasks.json 작성 — Task당 1개 명령으로 나누어 append

### 6. sds_create_tasks.py 실행

### 7. 결과 코멘트 게시 (jira_toolkit.py comment로 1개만)

## temp_tasks.json 작성 방법

**반드시 Task당 1개 명령으로 나누어 실행:**

```python
# 첫 번째 명령: 빈 리스트 초기화
python3 << 'PYEOF'
import pathlib, json
tasks = []
pathlib.Path('temp_tasks.json').write_text(json.dumps({"tasks": tasks}, ensure_ascii=False, indent=2))
print("Initialized temp_tasks.json")
PYEOF

# 두 번째 명령: 첫 번째 Task 추가 (Phase 1 — 의존성 없음)
python3 << 'PYEOF'
import pathlib, json
data = json.loads(pathlib.Path('temp_tasks.json').read_text(encoding='utf-8'))
data['tasks'].append({
    "summary": "[TASK-001] 공유 타입 및 인터페이스 정의",
    "description": "프로젝트 전체에서 사용하는 공유 타입 정의\n\n## 구현 대상\n- types/volume.ts: VolumeData, VoxelIndex, Dimensions\n- types/dicom.ts: DicomTags, DicomSlice, TransferSyntax\n- types/measurement.ts: Measurement, MeasurementType\n- interfaces/IRenderer.ts: IRenderer, IMprRenderer\n\n## 검증 기준\n- 모든 타입이 TypeScript 컴파일 에러 없이 정의\n- 인터페이스가 Detailed Design 명세와 일치",
    "phase": 1,
    "blocks": [],
    "implements_dd": ["PLAYG-XXXX"]
})
pathlib.Path('temp_tasks.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
print(f"Added task {len(data['tasks'])}")
PYEOF

# 세 번째 명령: 다음 Task 추가 (Phase 2 — Phase 1에 의존)
python3 << 'PYEOF'
import pathlib, json
data = json.loads(pathlib.Path('temp_tasks.json').read_text(encoding='utf-8'))
data['tasks'].append({
    "summary": "[TASK-002] DICOM 파일 파서 구현",
    "description": "DICOM 파일 로드, 매직 바이트 검증, 태그 파싱\n\n## 구현 대상\n- DicomFileLoader: File API 기반 로드\n- DicomTagReader: 태그 파싱\n- TransferSyntaxResolver: 전송 구문 처리\n- PixelDataDecoder: 픽셀 디코딩\n\n## 의존성\n- TASK-001 (공유 타입)\n\n## 검증 기준\n- 샘플 DICOM 파일 파싱 성공\n- 필수 태그 추출 확인\n- 비DICOM 파일 에러 처리",
    "phase": 2,
    "blocks": ["TASK-001"],
    "implements_dd": ["PLAYG-XXXX"]
})
pathlib.Path('temp_tasks.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
print(f"Added task {len(data['tasks'])}")
PYEOF

# ... 모든 Task를 추가할 때까지 계속
# 절대 빈 description으로 추가하지 마세요!
```

**주의:**
- **Task당 1개 명령**으로 나누어 실행
- **description은 절대 비워두지 마세요**
- Phase 번호에 맞춰 의존성 설정
- 모든 Detailed Design 티켓이 최소 1개 Task에 매핑되어야 함

## 스크립트 실행 (이 명령어 하나로 끝)

```bash
python3 goose_assets/runner/sds_create_tasks.py temp_tasks.json --sds {SDS_키} --project {PROJECT_KEY}
```

스크립트가 자동으로 처리하는 작업:
- Task 티켓 생성 (issuetype: Task)
- Blocks 링크 (Task → Task, 의존성)
- Implements 링크 (Task → Detailed Design)
- Relates 링크 (Task → SDS Document)

## 완성도 체크리스트

스크립트 실행 전 반드시 확인:
- [ ] 모든 Detailed Design 티켓이 최소 1개 Task에 매핑되었는가?
- [ ] 순환 의존성이 없는가?
- [ ] Phase 1 Task에 blocks가 비어있는가? (의존성 없음)
- [ ] 각 Task의 description에 구현 대상과 검증 기준이 포함되었는가?
- [ ] 빈 description이 없는가?

## 결과 보고

작업 완료 후 jira_toolkit.py로 현재 티켓에 결과 코멘트를 정확히 **1개만** 게시하세요.
코멘트에는:
- 생성된 Task 목록을 Phase별로 그룹화하여 표시
- 의존성 그래프 요약
- 총 Task 수

## 주의사항

- 프로젝트 키는 ticket_key에서 추출
- 이미 존재하는 Task는 중복 생성하지 않음
- 모든 내용은 한국어로 작성
- 치과 분야 의료기기에 맞게 내용 작성
