---
name: update
description: 티켓 내용을 수정합니다. 자연어로 전달된 수정 내용을 분석하여 적절한 필드를 업데이트합니다.
---

티켓 내용을 수정합니다. command_args로 전달된 자연어를 분석하여 적절한 필드를 업데이트합니다.

## 필수 작업

1. **현재 티켓 정보 확인**
   - context.json에서 ticket_key 확인
   - Jira API로 현재 티켓의 모든 필드값 조회
   - 이슈 타입 확인

2. **수정 내용 분석**
   - command_args로 전달된 자연어 수정 내용 파싱
   - 어떤 필드를 수정해야 할지 판단
   - 수정 전/후 비교

3. **티켓 업데이트**
   - jira_toolkit.py를 사용하여 필드 업데이트
   - 변경된 필드만 업데이트

4. **결과 코멘트 게시**
   - 수정 전/후 비교표를 코멘트로 게시

## Intended Use 티켓 필드

| 필드명 | 키 | 타입 | 설명 |
|--------|-----|------|------|
| Summary | summary | text | 제목 |
| Phase | customfield_10382 | select | PA, EA, ER, CA, M |
| Intended Purpose | customfield_10103 | textarea | 의도된 사용 목적 |
| Indication | customfield_10104 | textarea | 적응증 |
| Intended Patient Population | customfield_10105 | textarea | 대상 환자군 |
| Intended User | customfield_10106 | textarea | 예상 사용자 |
| Clinical Benefit | customfield_10107 | textarea | 임상적 이점 |
| User Constraint | customfield_10111 | textarea | 사용 제한사항 |
| Part of Body | customfield_10301 | text | 적용 부위 |
| Use Environment | customfield_10302 | text | 사용 환경 |
| Principle of Operation | customfield_10303 | text | 작동 원리 |
| Key Performance Spec | customfield_10304 | text | 주요 성능 사양 |
| Warnings and Precautions | customfield_10305 | textarea | 경고 및 주의사항 |

## 업데이트 방법

### 1. 필드 JSON 파일 생성
```bash
python3 -c "
import pathlib, json
fields = {
    'customfield_10103': '수정된 내용',
    'customfield_10104': '수정된 내용'
}
pathlib.Path('temp_fields.json').write_text(json.dumps(fields, ensure_ascii=False))
"
```

### 2. jira_toolkit.py로 업데이트
```bash
python3 goose_assets/runner/jira_toolkit.py update PLAYG-1962 temp_fields.json
```

## 수정 내용 분석 예시

### 예시 1: "사용 환경을 클라우드 환경도 지원하도록 수정해줘"
→ Use Environment (customfield_10302) 필드 수정
→ User Constraint (customfield_10111) 필드도 함께 검토

### 예시 2: "대상 환자를 성인으로 제한해줘"
→ Intended Patient Population (customfield_10105) 필드 수정

### 예시 3: "3D 렌더링 기능도 추가해줘"
→ Key Performance Spec (customfield_10304) 필드 수정
→ Principle of Operation (customfield_10303) 필드도 함께 검토

### 예시 4: "전체 내용을 다시 작성해줘"
→ 모든 필드 재작성

## 결과 코멘트 형식

```
✅ !update 완료

| 필드 | 수정 전 | 수정 후 |
|------|---------|---------|
| Use Environment | 치과 병/의원 진료실 | 치과 병/의원 진료실, 클라우드 환경 |

총 1개 필드 수정됨
```

## 주의사항

- 수정 전 반드시 현재 값을 조회하여 비교
- command_args가 비어있으면 오류 메시지 반환
- 모든 내용은 한국어로 작성
- 치과 분야 의료기기에 맞게 내용 유지
