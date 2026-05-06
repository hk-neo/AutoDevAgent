---
name: generate
description: 티켓 타입에 따라 완성된 문서를 생성합니다.
---

티켓 타입에 따라 완성된 문서를 생성합니다.

## 중요 규칙

- **오직 지정된 참조 소스만 사용하세요.** 다른 문서나 티켓을 임의로 참조하지 마세요.
- **할루시네이션 금지:** 컨텍스트에 없는 정보를 만들어내지 마세요. 모든 내용은 참조 소스에서 파생되어야 합니다.
- **관련 없는 내용 절대 금지:** Todo 앱, 퀴즈 앱, 대학 과제 등 현재 작업과 무관한 내용이 출력에 포함되면 안 됩니다.

## 필수 작업

1. **현재 티켓 정보 확인**
   - context.json에서 ticket_key 확인
   - Jira API로 티켓의 issuetype, summary, 필드값 확인

2. **template 파일 선택**
   - 티켓 타입에 따라 아래 template 파일을 읽어 지시사항을 따르세요:

| 티켓 타입 | 제목 패턴 | template 파일 | 생성물 |
|-----------|-----------|---------------|--------|
| Intended Use | - | `templates/intended-use.md` | IU 문서 |
| System Requirement | 각 요구사항별 | `templates/system-requirement.md` | SyRS 상세 |
| Document | [System Requirement Specification] | `templates/srs.md` | SRS 문서 |
| Document | [SW Architecture Document] | `templates/sad.md` | SAD 문서 |
| Document | [SW Detailed Design Document] | `templates/sds.md` | SDS 문서 |
| Document | [SW Development Plan] | `templates/sw-dev-plan.md` | SW Development Plan |
| Document | [Risk Management Plan] | `templates/risk-management-plan.md` | Risk Management Plan |
| Document | [Security Maintenance Plan] | `templates/security-maintenance-plan.md` | Security Maintenance Plan |
| Document | [Configuration Management Plan] | `templates/configuration-management-plan.md` | Configuration Management Plan |

   template 파일 경로: `goose_assets/skills/generate/templates/`

3. **template에 따라 문서 생성**
4. **GitHub에 커밋**
5. **Jira 코멘트로 결과 보고**

## 참조 경계 (매우 중요)

각 문서는 **자신의 template에 명시된 참조 소스만** 사용해야 합니다.
라이프사이클에서 **상위에 있는 문서는 하위 문서를 참조할 수 없습니다.** (아직 존재하지 않으므로)

```
IU → SyRS 순서이므로:
- IU 문서는 IU 티켓 필드만 참조 (SyRS 참조 금지)
- SyRS 문서는 IU만 참조 가능
- SRS 문서는 IU + SyRS 참조 가능
- SAD 문서는 SRS 참조 가능
- SDS 문서는 SRS + SAD 참조 가능

PA Plan 문서들은 같은 Gate의 IU + SyRS + Classification 참조:
- SW Development Plan: IU + Classification + SyRS
- Risk Management Plan: IU + Classification + SyRS
- Security Maintenance Plan: SyRS (Security) + IU
- Configuration Management Plan: IU + SyRS
```

## 문서 생성 위치

- `docs/{ticket_key}/` 디렉토리에 마크다운 파일로 생성
- 파일명: `{문서타입}.md` (예: `intended-use.md`, `srs.md`)
- 커밋 메시지: `[{TICKET_KEY}] Generate: {문서 타입}`

## 결과 보고

작업 완료 후 jira_toolkit.py로 현재 티켓에 결과 코멘트를 게시하세요.
코멘트에는:
- 생성된 문서 요약
- GitHub 커밋 링크
- 문서의 주요 내용 개요

디버그 정보는 포함하지 마세요.
