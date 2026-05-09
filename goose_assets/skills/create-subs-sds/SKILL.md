---
name: create-subs-sds
description: SDS Document에서 모듈 티켓을 생성합니다. SRS + SAD를 종합 분석하여 SOLID 원칙에 따른 상세 설계 모듈을 만듭니다.
---

SDS(SW Detailed Design Document)에서 모듈 티켓을 생성합니다.

**이 스킬은 sds_create_modules.py 스크립트만 사용합니다. 다른 방법은 사용하지 마세요.**

## ⚠️ 반드시 지켜야 할 규칙

1. **jira_toolkit.py create 절대 사용 금지** — 티켓 생성은 스크립트가 합니다
2. **직접 curl로 링크 금지** — 링크도 스크립트가 합니다
3. **Architecture 1:1 매핑 금지** — "[SDS] ARCH-001 상세 설계" 같은 티켓은 만들지 마세요
4. **반드시 sds_create_modules.py만 사용**

## 핵심 원칙

**SDS는 Architecture의 1:1 복사가 아닙니다.** SRS(요구사항) + SAD(아키텍처)를 모두 종합 분석하여 실제 구현 모듈로 분해합니다.

| ❌ 잘못된 접근 | ✅ 올바른 접근 |
|---|---|
| "[SDS-ARCH-001] 렌더링 파이프라인 상세 설계" | "[MOD-001] DICOM 파일 파서" |
| Architecture당 1개씩 1:1 매핑 | 여러 Architecture에 걸친 실제 구현 모듈 |
| SAD 내용만 참고 | **SRS + SAD 모두 종합 참고** |
| SAD 내용을 그대로 반복 | 클래스/함수 수준의 실제 설계 |
| 제목만 있는 빈 티켓 | **충실한 내용이 포함된 상세 티켓** |

### 설계 철학: SOLID 원칙 준수

- **S (Single Responsibility)**: 각 모듈은 하나의 명확한 책임만 가짐
- **O (Open/Closed)**: 확장에는 열려 있고 수정에는 닫혀 있는 구조
- **L (Liskov Substitution)**: 인터페이스 구현체는 서로 교체 가능
- **I (Interface Segregation)**: 모듈은 자신이 사용하지 않는 인터페이스에 의존하지 않음
- **D (Dependency Inversion)**: 상위 모듈이 하위 모듈에 직접 의존하지 않고 추상화에 의존

### 생각 방식

1. **전체 분석**: SRS의 모든 Requirement + SAD의 모든 Architecture를 동시에 분석
2. **구현 관점**: "이 시스템을 실제로 코딩하려면 어떤 모듈이 필요한가?"
3. **교차 참조**: 한 모듈이 여러 Architecture에 걸쳐 있을 수 있음
4. **분해**: 한 Architecture가 여러 모듈로 나뉠 수 있음
5. **충실한 내용**: 각 모듈의 description에 클래스, 메서드, 데이터 구조, 알고리즘, 에러 처리를 모두 포함

## 필수 작업

### 1. 현재 티켓 정보 확인
- context.json에서 ticket_key 확인
- Jira API로 티켓의 summary(제목)과 issuetype 확인

### 2. 컨텍스트 수집 (매우 중요 — SRS와 SAD 모두 필수)
- `docs/` 폴더에서 **SRS 문서** 읽기 (요구사항 전체 파악)
- `docs/` 폴더에서 **SAD 문서** 읽기 (아키텍처 전체 파악)
- Jira API로 **SRS Requirement 티켓들 전체 조회** (각 티켓의 description까지)
- Jira API로 **SAD Architecture 티켓들 전체 조회** (각 티켓의 description까지)

### 3. 모듈 분해 (8~15개)

**전체 프로젝트를 종합 분석하여 실제 구현 관점에서 모듈을 식별합니다.**

각 모듈의 description에 반드시 포함할 내용:

```
## 책임 (Single Responsibility)
이 모듈의 단일 책임 설명

## 클래스 설계
- ClassName: 역할 설명
  - 필드: ...
  - 메서드: ...

## 인터페이스 (Dependency Inversion)
- IInterfaceName: 추상화된 인터페이스 정의

## 데이터 구조
- 주요 타입/구조체/Enum 정의

## 알고리즘
- 핵심 알고리즘 설명 (의사코드 수준)

## 에러 처리
- 예외 상황 및 처리 방법

## 의존성
- 다른 모듈과의 관계

## 성능 목표
- 해당 모듈의 성능 요구사항
```

### 4. temp_modules.json 작성 — 모듈당 1개 명령으로 나누어 append

### 5. sds_create_modules.py 실행

### 6. 결과 코멘트 게시 (jira_toolkit.py comment로 1개만)

## temp_modules.json 작성 방법

**반드시 아래 방식으로 모듈당 1개 명령으로 나누어 실행:**

```python
# 첫 번째 명령: 빈 리스트 초기화
python3 << 'PYEOF'
import pathlib, json
modules = []
pathlib.Path('temp_modules.json').write_text(json.dumps({"modules": modules}, ensure_ascii=False, indent=2))
print("Initialized temp_modules.json")
PYEOF

# 두 번째 명령: 첫 번째 모듈 추가 (description을 충실하게 작성!)
python3 << 'PYEOF'
import pathlib, json
data = json.loads(pathlib.Path('temp_modules.json').read_text(encoding='utf-8'))
data['modules'].append({
    "summary": "[MOD-001] DICOM 파일 파서",
    "description": "DICOM 형식 CBCT 영상 파일의 로드, 파싱, 무결성 검증\n\n## 책임\n로컬 DICOM 파일의 로드 및 구조 해석, 메타데이터 추출, 픽셀 데이터 디코딩\n\n## 클래스 설계\n- DicomFileLoader: File API 기반 파일 로드 및 ArrayBuffer 변환\n- DicomTagReader: 메타헤더 매직 바이트 검증, 태그 파싱 (그룹/엘리먼트)\n- TransferSyntaxResolver: 전송 구문 UID 해석 및 디코딩 전략 선택\n- PixelDataDecoder: 압축/비압축 픽셀 데이터 디코딩\n\n## 인터페이스\n- IFileLoader: load(file) -> RawBuffer (추상화)\n- ITagParser: parse(buffer) -> DicomTags\n\n## 에러 처리\n- 비DICOM 파일: InvalidDicomError\n- 필수 태그 누락: MissingTagError\n- 미지원 전송 구문: UnsupportedTransferSyntaxError",
    "implements": ["PLAYG-2299", "PLAYG-2302"],
    "implements_req": ["PLAYG-2267"]
})
pathlib.Path('temp_modules.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
print(f"Added module {len(data['modules'])}")
PYEOF

# 세 번째 명령: 두 번째 모듈 추가
python3 << 'PYEOF'
import pathlib, json
data = json.loads(pathlib.Path('temp_modules.json').read_text(encoding='utf-8'))
data['modules'].append({
    "summary": "[MOD-002] Volume 데이터 빌더",
    "description": "DICOM 슬라이스를 3D Volume 데이터로 구성\n\n## 책임\n슬라이스 데이터를 3D Volume으로 변환, 보간, 메모리 관리\n\n## 클래스 설계\n- VolumeBuilder: 슬라이스 배열 -> VolumeData 변환 오케스트레이션\n- InterpolationEngine: 이중선형/삼중선형 보간\n- MemoryPool: ArrayBuffer 풀 관리, 재사용\n\n## 데이터 구조\n- VolumeData: { buffer: ArrayBuffer, dimensions: [x,y,z], spacing: [sx,sy,sz] }\n- VoxelIndex: { x: number, y: number, z: number }\n\n## 알고리즘\n- trilinearInterpolate(p, volume): 인접 8개 복셀 가중 평균\n\n## 성능 목표\n- 512³ 볼륨 구성 5초 이내",
    "implements": ["PLAYG-2299", "PLAYG-2302"],
    "implements_req": ["PLAYG-2267", "PLAYG-2276"]
})
pathlib.Path('temp_modules.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
print(f"Added module {len(data['modules'])}")
PYEOF

# ... 모든 모듈을 추가할 때까지 계속
# 절대 빈 description으로 추가하지 마세요!
# 각 모듈마다 충실한 내용을 반드시 포함하세요!
```

**주의:**
- 한 번에 모든 모듈을 넣지 말고 **모듈당 1개 명령**으로 나누어 실행
- **description은 절대 비워두지 마세요** — 클래스, 메서드, 에러 처리까지 충실하게
- 모듈을 빠뜨리지 마세요 — SRS의 모든 Requirement가 최소 1개 모듈에 매핑되어야 함

## 스크립트 실행 (이 명령어 하나로 끝)

```bash
python3 goose_assets/runner/sds_create_modules.py temp_modules.json --sds {SDS_키} --project {PROJECT_KEY}
```

스크립트가 자동으로 처리하는 작업:
- Module 티켓 생성 (issuetype: Task)
- Implements 링크 (Module → Architecture)
- Implements 링크 (Module → Requirement, 근거 추적)
- Relates 링크 (Module → SDS Document)

## 완성도 체크리스트

스크립트 실행 전 반드시 확인:
- [ ] SRS의 **모든** Requirement가 최소 1개 모듈의 implements_req에 포함되었는가?
- [ ] SAD의 **모든** Architecture가 최소 1개 모듈의 implements에 포함되었는가?
- [ ] 각 모듈의 description에 클래스 설계가 포함되었는가?
- [ ] 빈 description이 없는가?
- [ ] SOLID 원칙에 위배되는 모듈이 없는가?

## 결과 보고

작업 완료 후 jira_toolkit.py로 현재 티켓에 결과 코멘트를 정확히 **1개만** 게시하세요.
코멘트에는 생성된 티켓 목록을 표 형식으로 포함하세요.

## 주의사항

- 프로젝트 키는 ticket_key에서 추출 (예: PLAYG-2280 → PLAYG)
- 이미 존재하는 하위 티켓은 중복 생성하지 않음
- 모든 내용은 한국어로 작성
- 치과 분야 의료기기에 맞게 내용 작성
