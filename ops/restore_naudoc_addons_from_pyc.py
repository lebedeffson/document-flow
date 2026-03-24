#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
ADDONS_DIR = ROOT_DIR / "naudoc_project" / "Products" / "CMFNauTools" / "Addons"
VENV_UNCOMPYLE6 = Path.home() / "Code" / "venv" / "bin" / "uncompyle6"


def sanitize_module_source(py_path: Path, source: str) -> str:
    lines = source.splitlines()

    while lines and lines[-1].startswith("# okay decompiling "):
        lines.pop()
    while lines and not lines[-1].strip():
        lines.pop()

    if "skin" not in py_path.parts and lines and lines[-1].strip() == "return":
        lines.pop()
        while lines and not lines[-1].strip():
            lines.pop()

    return "\n".join(lines) + "\n"


def decompile_file(pyc_path: Path) -> tuple[bool, str]:
    py_path = pyc_path.with_suffix(".py")
    result = subprocess.run(
        [str(VENV_UNCOMPYLE6), str(pyc_path)],
        cwd=ROOT_DIR,
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "unknown uncompyle6 error"
        return False, message

    py_path.write_text(sanitize_module_source(py_path, result.stdout), encoding="utf-8")
    return True, str(py_path.relative_to(ROOT_DIR))


def main() -> int:
    if not ADDONS_DIR.exists():
        print(f"Addons directory not found: {ADDONS_DIR}", file=sys.stderr)
        return 1

    if not VENV_UNCOMPYLE6.exists():
        print(f"uncompyle6 not found: {VENV_UNCOMPYLE6}", file=sys.stderr)
        return 1

    pyc_files = sorted(ADDONS_DIR.rglob("*.pyc"))
    if not pyc_files:
        print("No .pyc files found under Addons")
        return 0

    restored = []
    failed = []

    for pyc_path in pyc_files:
        ok, message = decompile_file(pyc_path)
        if ok:
            restored.append(message)
            print(f"[ok] {message}")
        else:
            failed.append((pyc_path, message))
            print(f"[fail] {pyc_path.relative_to(ROOT_DIR)}: {message}", file=sys.stderr)

    print("")
    print(f"Restored: {len(restored)}")
    print(f"Failed: {len(failed)}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
