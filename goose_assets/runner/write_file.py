#!/usr/bin/env python3
"""파일 작성 헬퍼. 긴 내용을 안전하게 파일로 저장합니다.

사용법:
  python3 goose_assets/runner/write_file.py <파일경로>

stdin으로 내용을 받습니다. heredoc이나 python -c 대신 사용하세요.

예시:
  python3 -c "
  import pathlib
  content = '''# 제목
  긴 내용...
  '''
  pathlib.Path('/tmp/content.txt').write_text(content, encoding='utf-8')
  "
  python3 goose_assets/runner/write_file.py output.md < /tmp/content.txt

  또는 직접 파이프:
  echo '내용' | python3 goose_assets/runner/write_file.py output.md
"""
import sys
import pathlib

if len(sys.argv) < 2:
    print("Usage: python3 write_file.py <filepath>", file=sys.stderr)
    print("Content is read from stdin.", file=sys.stderr)
    sys.exit(1)

filepath = sys.argv[1]
content = sys.stdin.read()

pathlib.Path(filepath).parent.mkdir(parents=True, exist_ok=True)
pathlib.Path(filepath).write_text(content, encoding='utf-8')
print(f"Written {len(content)} chars to {filepath}", file=sys.stderr)
