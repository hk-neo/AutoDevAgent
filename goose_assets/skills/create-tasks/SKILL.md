---
name: create-tasks
description: SDS Detailed Design에서 Bottom-Up 순서로 구현 Task를 생성합니다.
---

## 절대 규칙

1. **jira_toolkit.py create 금지** — sds_create_tasks.py만 사용
2. **curl 금지** — 스크립트가 링크까지 처리
3. **한 명령에 Task 1개만** — 여러 개 넣으면 실패합니다

## 수행 단계

1. context.json에서 ticket_key 확인
2. Jira API로 SDS 티켓에 연결된 **Detailed Design 티켓들** 전체 조회
3. docs/에서 SRS, SAD 문서 참고
4. Bottom-Up으로 Task 분해

**Phase 순서:**
- Phase 1: 공유 타입, 인터페이스, UI 스펙 (의존성 없음)
- Phase 2: DICOM 파서, Volume 빌더
- Phase 3: MPR 렌더러, 3D 렌더러, 카메라
- Phase 4: 측정 도구, ROI, 뷰포트 동기화
- Phase 5: 앱 셸, 컴포넌트 조립, 상태 관리
- Phase 6: 보안 검증, 성능 최적화

5. 아래 명령으로 Task 1개씩 생성
6. 모든 Task 생성 후 link 명령으로 의존성 연결
7. summary 명령으로 코멘트용 요약 출력 후 jira_toolkit.py comment로 게시

## Task 생성 명령

```bash
# description이 짧으면 inline
python3 goose_assets/runner/sds_create_tasks.py add \
  --sds {SDS_키} --project {PROJECT_KEY} \
  --summary "[TASK-001] 공유 타입 정의" \
  --phase 1 --blocks "" --dd PLAYG-XXXX

# description이 길면 파일로 전달
python3 -c "
import pathlib
pathlib.Path('/tmp/task001.txt').write_text('구현 대상\\n- 타입 정의\\n- 인터페이스\\n\\n검증 기준\\n- 컴파일 에러 없음', encoding='utf-8')
"
python3 goose_assets/runner/sds_create_tasks.py add \
  --sds {SDS_키} --project {PROJECT_KEY} \
  --summary "[TASK-001] 공유 타입 정의" \
  --desc-file /tmp/task001.txt \
  --phase 1 --blocks "" --dd PLAYG-XXXX
```

**--blocks**: 선행 Task의 summary를 콤마로 구분 (Phase 1은 빈 문자열 "")
**--dd**: 이 Task가 구현할 Detailed Design 티켓 키

## 의존성 연결 (모든 Task 생성 후 1번만)

```bash
python3 goose_assets/runner/sds_create_tasks.py link --project {PROJECT_KEY}
```

## 코멘트용 요약

```bash
python3 goose_assets/runner/sds_create_tasks.py summary --sds {SDS_키}
```

이 출력을 jira_toolkit.py comment로 게시하세요.

## 완성도 체크

- 모든 Detailed Design이 최소 1개 Task에 매핑?
- Phase 1 Task에 blocks가 비어있음?
- 빈 description 없음?
