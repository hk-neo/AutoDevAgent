#!/usr/bin/env python3
"""
문서 생성 스크립트 — 섹션별로 조립

긴 문서를 한 번에 쓰면 tool argument 파싱 에러가 발생하므로,
섹션 단위로 나누어 조립합니다.

사용법:
  # 1. 문서 초기화
  python3 goose_assets/runner/generate_doc.py init \
    --title "Software Detailed Design Document" \
    --product "로컬 CBCT 웹 뷰어" \
    --project PLAYG --phase EA --output docs/sds.md

  # 2. 섹션 추가 (내용을 파일로 전달)
  python3 goose_assets/runner/generate_doc.py section \
    --file /tmp/sec_intro.txt

  python3 goose_assets/runner/generate_doc.py section \
    --file /tmp/sec_mod1.txt

  # 3. 완성 — Jira description 업데이트
  python3 goose_assets/runner/generate_doc.py finish \
    --ticket PLAYG-2280 --output docs/sds.md
"""

import json
import os
import sys
import pathlib
import functools

print = functools.partial(print, flush=True)

WORK_FILE = pathlib.Path('/tmp/_generate_doc.md')


def cmd_init(args):
    """문서 초기화"""
    title = product = project = phase = output = None

    i = 0
    while i < len(args):
        if args[i] == '--title' and i + 1 < len(args):
            title = args[i + 1]; i += 2
        elif args[i] == '--product' and i + 1 < len(args):
            product = args[i + 1]; i += 2
        elif args[i] == '--project' and i + 1 < len(args):
            project = args[i + 1]; i += 2
        elif args[i] == '--phase' and i + 1 < len(args):
            phase = args[i + 1]; i += 2
        elif args[i] == '--output' and i + 1 < len(args):
            output = args[i + 1]; i += 2
        else:
            i += 1

    if not title:
        print("Error: --title required")
        sys.exit(1)

    header = f"# {title}\n"
    if product:
        header += f"## {product}\n\n"
    header += "### 문서 정보\n\n"
    header += "| 항목 | 내용 |\n|------|------|\n"
    header += f"| 문서명 | {title} |\n"
    if product:
        header += f"| 제품명 | {product} |\n"
    if project:
        header += f"| 프로젝트 | {project} |\n"
    if phase:
        header += f"| Phase | {phase} |\n"
    header += "| 버전 | 1.0 |\n"
    header += f"\n---\n\n"

    WORK_FILE.write_text(header, encoding='utf-8')

    # output 경로 저장
    meta = {'output': output or 'docs/document.md'}
    pathlib.Path('/tmp/_generate_doc_meta.json').write_text(
        json.dumps(meta, ensure_ascii=False), encoding='utf-8'
    )

    print(f"Document initialized: {title}")
    print(f"Output will be: {output or 'docs/document.md'}")


def cmd_section(args):
    """섹션 추가"""
    section_file = None

    i = 0
    while i < len(args):
        if args[i] == '--file' and i + 1 < len(args):
            section_file = args[i + 1]; i += 2
        else:
            i += 1

    if not section_file:
        print("Error: --file required")
        sys.exit(1)

    content = pathlib.Path(section_file).read_text(encoding='utf-8')

    existing = WORK_FILE.read_text(encoding='utf-8') if WORK_FILE.exists() else ''
    existing += content + '\n\n'
    WORK_FILE.write_text(existing, encoding='utf-8')

    lines = content.strip().split('\n')
    first_line = lines[0][:60] if lines else '(empty)'
    print(f"Section added: {first_line}...")


def cmd_finish(args):
    """완성 — Jira 업데이트 + 파일 저장"""
    ticket_key = None
    output = None

    i = 0
    while i < len(args):
        if args[i] == '--ticket' and i + 1 < len(args):
            ticket_key = args[i + 1]; i += 2
        elif args[i] == '--output' and i + 1 < len(args):
            output = args[i + 1]; i += 2
        else:
            i += 1

    if not WORK_FILE.exists():
        print("Error: No document in progress. Run init first.")
        sys.exit(1)

    # meta에서 output 경로 읽기
    if not output:
        meta_path = pathlib.Path('/tmp/_generate_doc_meta.json')
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding='utf-8'))
            output = meta.get('output', 'docs/document.md')
        else:
            output = 'docs/document.md'

    content = WORK_FILE.read_text(encoding='utf-8')

    # 파일 저장
    out_path = pathlib.Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding='utf-8')
    print(f"Saved: {output} ({len(content)} chars)")

    # Jira description 업데이트
    if ticket_key:
        desc_path = pathlib.Path('temp_desc.json')
        desc_path.write_text(
            json.dumps({'description': content}, ensure_ascii=False),
            encoding='utf-8'
        )
        print(f"Run this to update Jira:")
        print(f"  python3 goose_assets/runner/jira_toolkit.py update {ticket_key} temp_desc.json")
    else:
        print("No --ticket specified, skipping Jira update")

    # 정리
    WORK_FILE.unlink(missing_ok=True)
    pathlib.Path('/tmp/_generate_doc_meta.json').unlink(missing_ok=True)

    print(f"\nDocument generation complete.")


def cmd_preview(args):
    """현재까지 작성된 내용 미리보기"""
    if not WORK_FILE.exists():
        print("No document in progress")
        return

    content = WORK_FILE.read_text(encoding='utf-8')
    lines = content.split('\n')
    print(f"--- Preview ({len(lines)} lines, {len(content)} chars) ---")
    # 앞 30줄만
    for line in lines[:30]:
        print(line)
    if len(lines) > 30:
        print(f"... ({len(lines) - 30} more lines)")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    subcmd = sys.argv[1]
    args = sys.argv[2:]

    if subcmd == 'init':
        cmd_init(args)
    elif subcmd == 'section':
        cmd_section(args)
    elif subcmd == 'finish':
        cmd_finish(args)
    elif subcmd == 'preview':
        cmd_preview(args)
    else:
        print(f"Unknown command: {subcmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
