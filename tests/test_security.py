import re
from pathlib import Path


def test_repository_contains_no_literal_api_keys():
    root = Path(__file__).parents[1]
    excluded = {".git", ".worktrees", ".venv", "outputs", "__pycache__"}
    patterns = [
        re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
        re.compile(r"DEEPSEEK_API_KEY\s*=\s*['\"][^'\"]+['\"]"),
    ]
    violations = []
    for path in root.rglob("*"):
        if not path.is_file() or any(part in excluded for part in path.parts):
            continue
        if path.suffix.lower() not in {".py", ".md", ".ipynb", ".txt", ".ini"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(pattern.search(text) for pattern in patterns):
            violations.append(str(path.relative_to(root)))
    assert violations == []
