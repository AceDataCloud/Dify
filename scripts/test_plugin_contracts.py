#!/usr/bin/env python3
"""Contract guards for AceDataCloud Dify plugins."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"


def is_callback_condition(node: ast.AST) -> bool:
    return any(isinstance(child, ast.Name) and child.id == "callback_url" for child in ast.walk(node))


def assigns_async_payload(node: ast.AST) -> bool:
    for child in ast.walk(node):
        if not isinstance(child, ast.Assign):
            continue
        for target in child.targets:
            if not isinstance(target, ast.Subscript) or not isinstance(target.value, ast.Name):
                continue
            key = target.slice.value if isinstance(target.slice, ast.Constant) else None
            if target.value.id == "payload" and key == "async":
                return True
    return False


def find_callback_gated_async() -> list[str]:
    findings: list[str] = []
    for path in sorted(PLUGINS.glob("*/tools/*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.If) and is_callback_condition(node.test):
                for child in node.body:
                    if assigns_async_payload(child):
                        findings.append(f"{path.relative_to(ROOT)}:{child.lineno}")
    return findings


def main() -> int:
    findings = find_callback_gated_async()
    if findings:
        print("async payload must not depend on callback_url:", file=sys.stderr)
        for finding in findings:
            print(f"- {finding}", file=sys.stderr)
        return 1
    print("plugin async contract checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
