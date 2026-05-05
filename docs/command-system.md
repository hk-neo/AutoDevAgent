# Command System

Jira 티켓의 코멘트를 통해 작동하는 명령어 시스템입니다.

## 명령어 목록

| 명령어 | 설명 |
|--------|------|
| **!generate** | 현재 티켓에 맞는 산출물/코드 생성 |
| **!create-subs** | 하위 티켓 생성 |
| **!create-tasks** | 구현 태스크 생성 |
| **!traceability** | 추적성 확인/검증 |
| **!update** | 티켓 내용 수정 |
| **!help** | 도움말/사용법 |

---

## !generate

현재 티켓에 맞는 것을 생성합니다.

### 티켓 타입별 동작

| 티켓 타입 | 생성물 | 참조 소스 |
|-----------|--------|----------|
| **System Requirement Document** | SRS 문서 | 하위 티켓들 |
| **SRS Document** | SAD 문서 | Github의 SRS |
| **SAD Document** | SDS 문서 | Github의 SRS, SAD |

### 사용 예시

```jira
# 기본 사용
!generate

# 포맷 지정 (선택사항)
!generate --format=pdf
```

---

## !create-subs

하위 티켓들을 생성합니다.

### 티켓 타입별 동작

| 티켓 타입 | 생성 대상 | 비고 |
|-----------|----------|------|
| **Gate** | 해당 Phase의 빈 Document 티켓들 | 제목만 설정 |
| **Document (Intended Use)** | IU 티켓들 | 내용+링크 포함 |
| **Document (System Req)** | System Requirement 티켓들 | 상위 문서들 참고, 링크 포함 |
| **Document (SRS)** | SDS/Architecture 티켓들 | |

### 사용 예시

```jira
# 기본 사용
!create-subs

# 자연어로 세부 전달
!create-subs CBCT 웹 뷰어 - 로컬 데이터만 지원
```

---

## !create-tasks

구현을 위한 태스크들을 생성합니다.

### 사용 위치
- SDS (Detailed Design) Document

### 생성 방식
- Bottom-Up 순서: 부품부터 조립까지
- 의존성 분석 기반

### 사용 예시

```jira
# 기본 사용
!create-tasks
```

---

## !traceability

추적성을 확인하고 관리합니다.

### 하위 명령어

| 명령어 | 설명 |
|--------|------|
| (기본) | 현재 티켓의 추적성 상태 확인 |
| `--find-missing` | 누락된 링크 찾기 |
| `--fix` | 누락된 링크 자동 생성 제안 |
| `--project` | 전체 프로젝트 추적성 현황 |

### 사용 예시

```jira
# 기본 사용
!traceability

# 누락된 링크 찾기
!traceability --find-missing

# 자동 링크 제안
!traceability --fix

# 전체 현황
!traceability --project
```

---

## !update

티켓 내용을 수정합니다.

### 기본 동작

```jira
# 현재 티켓만 수정
!update "내용 수정"
```

### 옵션

| 옵션 | 설명 |
|------|------|
| `--preview` | 미리보기만 (실제 수정 안 함) |
| `--cascade` | 연쇄 수정 활성화 |
| `--direction={up,down,both}` | 전파 방향 |
| `--depth={1,2,3,...}` | 전파 깊이 |

### 사용 예시

```jira
# 기본 사용 (현재 티켓만)
!update "사용자 로그인 기능 추가해줘"

# 미리보기
!update --preview "내용 수정"

# 연쇄 수정 (자동 감지)
!update --cascade

# 방향과 깊이 지정
!update --cascade both 2 "내용 수정"
```

### 연쇄 수정 방향

```
상위(UP) ← 현재 → 하위(DOWN)
```

- `direction=up`: 상위만 (1단계)
- `direction=down`: 하위만 (1단계)
- `direction=both`: 양방향
- `depth`: 몇 단계까지 전파할지

---

## !help

도움말을 표시합니다.

### 사용 예시

```jira
# 전체 명령어 목록
!help

# 특정 명령어 사용법
!help update
!help traceability
```

---

## 라이프사이클 흐름

### PA Phase 예시

```
1. PA Gate 생성 (사용자 직접)
   제목: "PA"

2. PA Gate에서
   !create-subs
   → PA 단계 Document들 생성 (빈 티켓)

3. Intended Use Document에서
   !create-subs CBCT 웹 뷰어 - 로컬 데이터만 지원
   → IU 티켓 생성 (내용+링크 포함)

4. System Requirement Document에서
   !create-subs
   → System Requirement 티켓들 생성 (IU 등 참고)

5. System Requirement Document에서
   !generate
   → SRS 문서 생성 + GitHub push

6. SRS Document에서
   !generate
   → SAD 문서 생성 + GitHub push

7. SAD Document에서
   !generate
   → SDS 문서 생성 + GitHub push

8. SDS Document에서
   !create-tasks
   → 구현 태스크들 생성 (Bottom-Up)

9. 각 태스크 구현 완료
```

---

## 추적성 링크 관계

```
Intended Use Document
  └─ is parent of → IU-1, IU-2, IU-3...

System Requirement Document
  └─ is parent of → SR-1, SR-2, SR-3...
      └─ relates to → IU-1, IU-2...

SRS Document
  └─ is parent of → SDS-1, SDS-2...
      └─ implements → SR-1, SR-2...
```

---

## 연쇄 수정 예시

```jira
# IU-1에서
!update --cascade both 2 "기능 추가"

# 영향 분석 (미리보기)
현재 티켓: IU-1
상위: 없음
하위:
  ├─ SR-1, SR-2, SR-3
  │   └─ 하위: SRS-1, SRS-2
  │       └─ 하위: SDS-1, SDS-2, SDS-3
  │           └─ 하위: TASK-01 ~ TASK-15

총 영향: 23개 티켓
수정할까요? (y/n)
```

---

## 주의사항

1. **미리보기 권장**: !update --cascade는 먼저 --preview로 확인 후 사용하세요.
2. **안전장치**: 옵션을 지정하지 않으면 기본 동작만 수행됩니다.
3. **도움말**: 복잡한 옵션은 !help로 확인하세요.
