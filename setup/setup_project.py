#!/usr/bin/env python3
"""
프로젝트 레포에 AutoDevAgent 환경 설정

사용법:
  # 타겟 레포 디렉토리에서 실행
  cd /path/to/my-project
  python3 /path/to/AutoDevAgent/setup/setup_project.py --project PLAYG

  # 또는 경로 지정
  python3 /path/to/AutoDevAgent/setup/setup_project.py --project PLAYG --repo /path/to/my-project

수행 작업:
  1. AutoDevAgent를 git submodule로 추가
  2. .claude/commands/ 생성 (implement, jira-read, jira-comment)
  3. .env 템플릿 생성
  4. .gitignore 업데이트
"""

import os
import sys
import pathlib
import subprocess
import functools

print = functools.partial(print, flush=True)

AUTODEVAGENT_REPO = 'https://github.com/hk-neo/AutoDevAgent.git'
AUTODEVAGENT_REPO_SSH = 'git@github.com:hk-neo/AutoDevAgent.git'

COMMANDS_DIR = '.claude/commands'


def get_autodevagent_dir():
    """이 스크립트의 위치에서 AutoDevAgent 루트 찾기"""
    script_dir = pathlib.Path(__file__).resolve().parent
    return script_dir.parent  # setup/ -> AutoDevAgent/


def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"  Warning: {result.stderr.strip()[:100]}")
    return result.returncode == 0


def setup_submodule(repo_dir):
    """AutoDevAgent을 서브모듈로 추가"""
    repo = pathlib.Path(repo_dir)

    if (repo / 'AutoDevAgent').exists():
        print("AutoDevAgent submodule already exists, skipping.")
        return True

    print("Adding AutoDevAgent as git submodule...")

    # SSH 또는 HTTPS 중 선택
    remote_url = AUTODEVAGENT_REPO
    ok = run_cmd(f'git submodule add {remote_url} AutoDevAgent', cwd=repo_dir)
    if not ok:
        # HTTPS 실패 시 SSH 시도
        ok = run_cmd(f'git submodule add {AUTODEVAGENT_REPO_SSH} AutoDevAgent', cwd=repo_dir)

    if ok:
        print("  Submodule added.")
    else:
        print("  Failed to add submodule. You can add it manually:")
        print(f"    git submodule add {remote_url} AutoDevAgent")

    return ok


def setup_claude_commands(repo_dir, project_key):
    """.claude/commands/ 생성"""
    repo = pathlib.Path(repo_dir)
    commands_dir = repo / COMMANDS_DIR
    commands_dir.mkdir(parents=True, exist_ok=True)

    # implement.md
    (commands_dir / 'implement.md').write_text(f"""---
project_key: {project_key}
---

Task 티켓을 읽고 코드를 구현합니다.

## 사용법
/implement PLAYG-2368

## 수행 단계

1. **티켓 정보 조회**
```bash
source .env 2>/dev/null; export $(grep -v '^#' .env | xargs) 2>/dev/null
python3 AutoDevAgent/goose_assets/runner/jira_toolkit.py fetch_linked {{"ticket_key"}}
```

2. **티켓 내용 분석**
   - summary, description 읽기
   - 연결된 Detailed Design 티켓 조회 (implements_dd)
   - 설계 내용 파악

3. **코드 구현**
   - 티켓 설명에 명시된 클래스/함수 구현
   - 관련 기존 코드 파악 후 일관성 유지
   - 타입스크립트/프로젝트 컨벤션 준수

4. **테스트**
   - 구현한 코드의 기본 동작 확인
   - 빌드 에러 없는지 확인

5. **커밋**
```bash
git add -A
git commit -m "[{{ticket_key}}] Implement: {{요약}}"
```

6. **Jira 업데이트**
```bash
source .env 2>/dev/null; export $(grep -v '^#' .env | xargs) 2>/dev/null
python3 AutoDevAgent/goose_assets/runner/jira_toolkit.py comment {{"ticket_key"}} "구현 완료: {{요약}}"
```
""", encoding='utf-8')

    # jira-read.md
    (commands_dir / 'jira-read.md').write_text("""---
---

Jira 티켓 정보를 조회합니다.

## 사용법
/jira-read PLAYG-2368

## 실행
```bash
source .env 2>/dev/null; export $(grep -v '^#' .env | xargs) 2>/dev/null
python3 AutoDevAgent/goose_assets/runner/jira_toolkit.py fetch_linked {{arg1}}
```

조회된 정보를 분석해서 요약해주세요.
""", encoding='utf-8')

    # jira-comment.md
    (commands_dir / 'jira-comment.md').write_text("""---
---

Jira 티켓에 코멘트를 게시합니다.

## 사용법
/jira-comment PLAYG-2368 구현 완료

## 실행
```bash
source .env 2>/dev/null; export $(grep -v '^#' .env | xargs) 2>/dev/null
python3 AutoDevAgent/goose_assets/runner/jira_toolkit.py comment {{arg1}} "{{args}}"
```
""", encoding='utf-8')

    # generate-tests.md
    (commands_dir / 'generate-tests.md').write_text(f"""---
project_key: {{project_key}}
---

Xray Cucumber 시나리오를 기반으로 Puppeteer 테스트 코드를 생성합니다.

## 사용법
/generate-tests PLAYG-2475

## 수행 단계

1. **Xray 인증 및 Test 키 조회**
```bash
source .env 2>/dev/null; export $(grep -v '^#' .env | xargs) 2>/dev/null
python3 AutoDevAgent/goose_assets/runner/xray_toolkit.py get_test_keys $ARGUMENTS
```

2. **Cucumber Feature Export**
```bash
python3 AutoDevAgent/goose_assets/runner/xray_toolkit.py export_cucumber "PLAYG-XXXX;PLAYG-YYYY;..." --output tests/xray
```

3. **Feature 파일 분석**
   - 각 `.feature` 파일 읽기
   - `@TEST_PLAYG-XXXX` 태그에서 테스트 키 추출
   - Given/When/Then 시나리오 분석

4. **테스트 코드 생성**
   - `tests/xray/` 디렉토리 생성
   - 이미 존재하는 파일은 건너뛰기 (수동 수정 보호)
   - 각 Test 키별 `tests/xray/PLAYG-XXXX.mjs` 생성
   - `tests/xray/helper.mjs` 공통 유틸리티 생성

5. **커밋**
```bash
git add tests/xray/
git commit -m "[$ARGUMENTS] Generate: Xray test scripts"
```
""", encoding='utf-8')

    # run-execution.md
    (commands_dir / 'run-execution.md').write_text(f"""---
project_key: {{project_key}}
---

Test Execution에 연결된 테스트 스크립트를 실행하고 결과를 Xray에 등록합니다.

## 사용법
/run-execution PLAYG-2475

## 수행 단계

1. **Xray 인증 및 Test 키 조회**
```bash
source .env 2>/dev/null; export $(grep -v '^#' .env | xargs) 2>/dev/null
python3 AutoDevAgent/goose_assets/runner/xray_toolkit.py get_test_keys $ARGUMENTS
```

2. **Vite Dev Server 확인**
```bash
curl -s http://localhost:5175 > /dev/null 2>&1 && echo "running" || echo "not running"
```
   - 실행 중이 아니면 `npx vite --port 5175 &` 로 시작

3. **테스트 스크립트 실행**
   - 조회된 Test 키별로 `tests/xray/PLAYG-XXXX.mjs` 실행
   - 스크립트가 없으면 SKIPPED 처리
   - 각 결과에서 PASSED/FAILED/SKIPPED 수집

4. **Xray 결과 등록**
```bash
python3 AutoDevAgent/goose_assets/runner/xray_toolkit.py import_results --results-json '{{"testExecutionKey":"$ARGUMENTS","tests":[...]}}'
```

5. **Jira 코멘트 등록**
```bash
python3 AutoDevAgent/goose_assets/runner/jira_toolkit.py comment $ARGUMENTS "테스트 실행 완료: PASSED X건, FAILED X건, SKIPPED X건 (총 X건)"
```
""", encoding='utf-8')

    print(f"Created .claude/commands/ (implement, jira-read, jira-comment, generate-tests, run-execution)")


def setup_env(repo_dir, project_key):
    """.env 템플릿 생성"""
    repo = pathlib.Path(repo_dir)
    env_path = repo / '.env'

    if env_path.exists():
        print(".env already exists, skipping.")
        return

    env_path.write_text(f"""# Jira Configuration
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
JIRA_PROJECT={project_key}

# Xray Configuration
XRAY_CLIENT_ID=your-xray-client-id
XRAY_CLIENT_SECRET=your-xray-client-secret

# GitHub Configuration
GITHUB_TOKEN=your-github-token
""", encoding='utf-8')

    print("Created .env template. Edit with your credentials.")


def setup_gitignore(repo_dir):
    """.gitignore 업데이트"""
    repo = pathlib.Path(repo_dir)
    gitignore_path = repo / '.gitignore'

    additions = ['.env']

    existing = ''
    if gitignore_path.exists():
        existing = gitignore_path.read_text(encoding='utf-8')

    new_lines = []
    for line in additions:
        if line not in existing:
            new_lines.append(line)

    if new_lines:
        with open(gitignore_path, 'a', encoding='utf-8') as f:
            f.write('\n# AutoDevAgent\n')
            for line in new_lines:
                f.write(f'{line}\n')
        print(f"Updated .gitignore ({len(new_lines)} entries added)")
    else:
        print(".gitignore already up to date.")


def main():
    project_key = None
    repo_dir = None

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--project' and i + 1 < len(sys.argv):
            project_key = sys.argv[i + 1]; i += 2
        elif sys.argv[i] == '--repo' and i + 1 < len(sys.argv):
            repo_dir = sys.argv[i + 1]; i += 2
        else:
            i += 1

    if not project_key:
        print("Usage: setup_project.py --project PROJECT_KEY [--repo REPO_DIR]")
        print("Example: setup_project.py --project PLAYG --repo /path/to/target-repo")
        sys.exit(1)

    if not repo_dir:
        repo_dir = os.getcwd()

    if not pathlib.Path(repo_dir / '.git').exists() if isinstance(repo_dir, pathlib.Path) else not pathlib.Path(f'{repo_dir}/.git').exists():
        print(f"Error: {repo_dir} is not a git repository")
        sys.exit(1)

    print(f"Setting up AutoDevAgent for project: {project_key}")
    print(f"Target repo: {repo_dir}")
    print(f"{'='*40}")

    setup_submodule(repo_dir)
    setup_claude_commands(repo_dir, project_key)
    setup_env(repo_dir, project_key)
    setup_gitignore(repo_dir)

    print(f"\n{'='*40}")
    print("Setup complete!")
    print(f"\nNext steps:")
    print(f"1. Edit .env with your Jira and Xray credentials")
    print(f"2. Open this repo in Claude Code")
    print(f"3. Use /implement PLAYG-XXXX to implement a task")
    print(f"4. Use /generate-tests PLAYG-XXXX to generate test scripts")
    print(f"5. Use /run-execution PLAYG-XXXX to run tests and report to Xray")


if __name__ == '__main__':
    main()
