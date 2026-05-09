---
name: create-tasks
description: SDS Detailed Design에서 Bottom-Up 순서로 구현 Task를 생성합니다.
---

## 절대 규칙

1. **jira_toolkit.py create 금지** — sds_create_tasks.py만 사용
2. **curl 금지** — 스크립트가 링크까지 처리
3. **한 명령에 Task 1개만** — 여러 개 넣으면 파싱 에러로 실패합니다

## 수행 단계

1. context.json에서 ticket_key 확인
2. Jira API로 SDS 티켓에 연결된 **Detailed Design 티켓들** 전체 조회 (description까지)
3. docs/에서 SRS, SAD 문서 참고
4. Bottom-Up으로 Task 분해 (의존성 없는 것부터)

**Bottom-Up 순서:**
- Phase 1: 공유 타입, 인터페이스, UI 컴포넌트 스펙 (의존성 없음)
- Phase 2: DICOM 파서, Volume 빌더 (Phase 1 의존)
- Phase 3: MPR 렌더러, 3D 렌더러, 카메라 (Phase 2 의존)
- Phase 4: 측정 도구, ROI, 뷰포트 동기화 (Phase 3 의존)
- Phase 5: 앱 셸, 컴포넌트 조립, 상태 관리 (Phase 4 의존)
- Phase 6: 보안 검증, 성능 최적화 (Phase 5 의존)

5. temp_tasks.json에 **Task 1개당 shell 명령 1개**로 append
6. sds_create_tasks.py 실행
7. jira_toolkit.py comment로 결과 보고 (1개만)

## temp_tasks.json 작성 (반드시 이 방식만 사용)

```bash
# 1단계: 초기화
python3 << 'PYEOF'
import pathlib, json
pathlib.Path('temp_tasks.json').write_text(json.dumps({"tasks": []}, ensure_ascii=False, indent=2))
print("Initialized")
PYEOF

# 2단계: Task 1개 추가 (이 패턴을 반복)
python3 << 'PYEOF'
import pathlib, json
data = json.loads(pathlib.Path('temp_tasks.json').read_text(encoding='utf-8'))
data['tasks'].append({
    "summary": "[TASK-001] 공유 타입 정의",
    "description": "구현 대상과 검증 기준을 포함한 설명",
    "phase": 1,
    "blocks": [],
    "implements_dd": ["PLAYG-XXXX"]
})
pathlib.Path('temp_tasks.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
print(f"Added task {len(data['tasks'])}")
PYEOF

# 3단계: Task 1개 추가 (계속 반복)
python3 << 'PYEOF'
import pathlib, json
data = json.loads(pathlib.Path('temp_tasks.json').read_text(encoding='utf-8'))
data['tasks'].append({
    "summary": "[TASK-002] DICOM 파일 파서 구현",
    "description": "구현 대상과 검증 기준을 포함한 설명",
    "phase": 2,
    "blocks": ["[TASK-001] 공유 타입 정의"],
    "implements_dd": ["PLAYG-XXXX"]
})
pathlib.Path('temp_tasks.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
print(f"Added task {len(data['tasks'])}")
PYEOF
```

**blocks 필드**: 선행 Task의 summary 문자열을 넣으세요. 스크립트가 자동으로 키를 찾아 연결합니다.

## 스크립트 실행

```bash
python3 goose_assets/runner/sds_create_tasks.py temp_tasks.json --sds {SDS_키} --project {PROJECT_KEY}
```

## 완성도 체크

- 모든 Detailed Design이 최소 1개 Task에 매핑?
- 순환 의존성 없음?
- 빈 description 없음?

## 결과 보고

jira_toolkit.py comment로 **1개만** 게시. Phase별로 그룹화하여 표시.
