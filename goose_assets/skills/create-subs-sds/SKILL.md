---
name: create-subs-sds
description: SDS Document에서 모듈 티켓을 생성합니다. 프로젝트 전체를 종합 분석하여 실제 구현 단위 모듈을 만듭니다.
---

SDS(SW Detailed Design Document)에서 모듈 티켓을 생성합니다.

**이 스킬은 sds_create_modules.py 스크립트만 사용합니다. 다른 방법은 사용하지 마세요.**

## ⚠️ 반드시 지켜야 할 규칙

1. **jira_toolkit.py create 절대 사용 금지** — 티켓 생성은 스크립트가 합니다
2. **직접 curl로 링크 금지** — 링크도 스크립트가 합니다
3. **Architecture 1:1 매핑 금지** — "[SDS] ARCH-001 상세 설계" 같은 티켓은 만들지 마세요
4. **반드시 sds_create_modules.py만 사용**

## 핵심 원칙

**SDS는 Architecture의 1:1 복사가 아닙니다.** 전체 프로젝트를 종합 분석하여 실제 구현 모듈로 분해합니다.

| ❌ 잘못된 접근 | ✅ 올바른 접근 |
|---|---|
| "[SDS-ARCH-001] 렌더링 파이프라인 상세 설계" | "[MOD-001] DICOM 파일 파서" |
| Architecture당 1개씩 1:1 매핑 | 여러 Architecture에 걸친 실제 구현 모듈 |
| SAD 내용을 그대로 반복 | 클래스/함수 수준의 실제 설계 |

**생각 방식:**
1. 전체 SRS Requirements + 전체 SAD Architectures를 동시에 분석
2. "이 시스템을 실제로 코딩하려면 어떤 모듈이 필요한가?" 관점
3. 한 모듈이 여러 Architecture에 걸쳐 있을 수 있음
4. 한 Architecture가 여러 모듈로 나뉠 수 있음

## 필수 작업

1. **현재 티켓 정보 확인**
   - context.json에서 ticket_key 확인
   - Jira API로 티켓의 summary(제목)과 issuetype 확인

2. **컨텍스트 수집**
   - `docs/` 폴더에서 SRS, SAD 문서 읽기
   - Jira API로 SRS Requirement 티켓들 전체 조회
   - Jira API로 SAD Architecture 티켓들 전체 조회

3. **모듈 분해** (8~15개)
   - 전체 프로젝트를 종합 분석
   - 실제 코딩 관점에서 모듈 식별
   - 각 모듈에 클래스/함수 수준 설계 포함

4. **temp_modules.json 작성** — 모듈당 1개 명령으로 나누어 append

5. **sds_create_modules.py 실행**

6. **결과 코멘트 게시** (jira_toolkit.py comment로 1개만)

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

# 두 번째 명령: 첫 번째 모듈 추가
python3 << 'PYEOF'
import pathlib, json
data = json.loads(pathlib.Path('temp_modules.json').read_text(encoding='utf-8'))
data['modules'].append({
    "summary": "[MOD-001] DICOM 파일 파서",
    "description": "DICOM 파일 로드, 파싱, 무결성 검증\n\n## 클래스\n- DicomFileLoader\n- DicomTagReader\n- PixelDataDecoder\n\n## 주요 메서드\n- loadFile(file): 파일 로드\n- validateMagicBytes(buffer): 검증",
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
    "description": "DICOM 슬라이스 → 3D Volume 구성\n\n## 클래스\n- VolumeBuilder\n- InterpolationEngine\n- MemoryPool",
    "implements": ["PLAYG-2299", "PLAYG-2302"],
    "implements_req": ["PLAYG-2267", "PLAYG-2276"]
})
pathlib.Path('temp_modules.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
print(f"Added module {len(data['modules'])}")
PYEOF

# ... 모든 모듈을 추가할 때까지 계속
```

## 스크립트 실행 (이 명령어 하나로 끝)

```bash
python3 goose_assets/runner/sds_create_modules.py temp_modules.json --sds {SDS_키} --project {PROJECT_KEY}
```

스크립트가 자동으로 처리하는 작업:
- Module 티켓 생성 (issuetype: Task)
- Implements 링크 (Module → Architecture)
- Implements 링크 (Module → Requirement, 근거 추적)
- Relates 링크 (Module → SDS Document)

## 결과 보고

작업 완료 후 jira_toolkit.py로 현재 티켓에 결과 코멘트를 정확히 **1개만** 게시하세요.
코멘트에는 생성된 티켓 목록을 표 형식으로 포함하세요.

## 주의사항

- 프로젝트 키는 ticket_key에서 추출 (예: PLAYG-2280 → PLAYG)
- 이미 존재하는 하위 티켓은 중복 생성하지 않음
- 모든 내용은 한국어로 작성
- 치과 분야 의료기기에 맞게 내용 작성
