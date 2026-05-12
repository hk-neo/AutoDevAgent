# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AutoDevAgent는 Jira 기반 의료기기 소프트웨어 개발 자동화 도구입니다. IEC 62304 라이프사이클에 맞춰 문서 생성, 추적성 관리, 구현 태스크 생성 등을 자동화합니다.

## Architecture

```
AutoDevAgent/
├── goose_assets/
│   ├── config/          # 프로젝트 설정 (config.yaml)
│   ├── runner/          # Python 실행 스크립트
│   │   ├── jira_toolkit.py    # Jira API 툴킷 (fetch/create/update/comment)
│   │   ├── generate_doc.py    # 문서 생성
│   │   ├── sds_create_tasks.py # 태스크 생성
│   │   ├── sds_create_modules.py # 모듈 생성
│   │   ├── sad_create_architectures.py # 아키텍처 생성
│   │   └── ...
│   └── skills/          # 스킬 정의 (SKILL.md)
│       ├── implement/    # 구현 스킬
│       ├── traceability/ # 추적성 스킬
│       ├── create-tasks/ # 태스크 생성 스킬
│       ├── create-subs/  # 하위 티켓 생성 스킬
│       ├── generate/     # 문서 생성 스킬
│       ├── plan/         # 계획 스킬
│       ├── update/       # 업데이트 스킬
│       └── help/         # 도움말 스킬
├── config/              # 프로젝트 매핑 설정
├── docs/                # 문서
├── scripts/             # 유틸리티 스크립트
└── setup/               # 프로젝트 초기화
```

## Key Workflows

### 추적성 체인 (Traceability)
```
SyRS (System Requirement) → MOD (Module Design) → TASK (Implementation)
       ↑__________________________|__________________________|
```
- SyRS ─Implements→ MOD (설계가 요구사항 구현)
- MOD ─Implements→ TASK (구현이 설계 구현)
- SyRS ─Implements→ TASK (요구사항 직접 추적)

### Jira Toolkit 사용법
```bash
source .env; export $(grep -v '^#' .env | xargs)
python3 goose_assets/runner/jira_toolkit.py fetch_linked TICKET_KEY
python3 goose_assets/runner/jira_toolkit.py comment TICKET_KEY "메시지"
python3 goose_assets/runner/jira_toolkit.py update TICKET_KEY fields.json
```

## Environment Variables

`.env` 파일에 다음 변수 필요:
- `JIRA_URL`: Jira 인스턴스 URL
- `JIRA_EMAIL`: Jira 계정 이메일
- `JIRA_API_TOKEN`: Jira API 토큰
- `JIRA_PROJECT`: 프로젝트 키 (예: PLAYG)
