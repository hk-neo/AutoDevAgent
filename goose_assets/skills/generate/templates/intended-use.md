# Intended Use 문서 생성

## 참조 소스

**오직 아래만 참조하세요:**
- 현재 Intended Use 티켓의 필드값 (Jira API로 조회)

**절대 참조하지 마세요:**
- System Requirement 티켓 (아직 생성되지 않았을 수 있음)
- SRS, SAD, SDS 문서
- GitHub의 다른 문서

## 수행 단계

1. Jira API로 현재 IU 티켓의 모든 필드값 조회
2. 필드값을 바탕으로 IU 문서 작성
3. docs/{ticket_key}/intended-use.md 로 저장
4. Git 커밋
5. Jira 코멘트로 결과 보고

## 문서 구조

```markdown
# Intended Use

## 1. 제품명
{summary 필드값}

## 2. 의도된 사용 목적 (Intended Purpose)
{customfield_10103 필드값}

## 3. 적응증 (Indication)
{customfield_10104 필드값}

## 4. 대상 환자군 (Intended Patient Population)
{customfield_10105 필드값}

## 5. 예상 사용자 (Intended User)
{customfield_10106 필드값}

## 6. 임상적 이점 (Clinical Benefit)
{customfield_10107 필드값}

## 7. 사용 제한사항 (User Constraint)
{customfield_10111 필드값}

## 8. 적용 부위 (Part of Body)
{customfield_10301 필드값}

## 9. 사용 환경 (Use Environment)
{customfield_10302 필드값}

## 10. 작동 원리 (Principle of Operation)
{customfield_10303 필드값}

## 11. 주요 성능 사양 (Key Performance Spec)
{customfield_10304 필드값}

## 12. 경고 및 주의사항 (Warnings and Precautions)
{customfield_10305 필드값}
```

## 작성 규칙

- 각 섹션은 해당 필드값을 기반으로 **확장**하여 작성
- 단순 필드 복사가 아닌, 문서 형태로 자연스럽게 전개
- MDR 규정에 부합하는 형식
- 치과 분야 의료기기 컨텍스트 유지
- 한국어로 작성
