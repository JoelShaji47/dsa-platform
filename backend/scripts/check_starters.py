import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.seeds import PROBLEMS

JAVAC = shutil.which("javac")
GPP = shutil.which("g++")


def check_python(slug, source, errors):
    try:
        compile(source, f"{slug}.py", "exec")
    except SyntaxError as exc:
        errors.append(f"[py] {slug}: {exc}")


def check_java(slug, source, tmp, errors):
    if JAVAC is None:
        return
    problem_dir = tmp / slug.replace("-", "_")
    problem_dir.mkdir(parents=True, exist_ok=True)
    java_file = problem_dir / "Main.java"
    java_file.write_text(source, encoding="utf-8")
    proc = subprocess.run(
        [JAVAC, "-d", str(problem_dir), str(java_file)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        errors.append(f"[java] {slug}:\n{proc.stderr.strip()[:500]}")
    else:
        shutil.rmtree(problem_dir, ignore_errors=True)


# Apple Clang (macOS) does not ship <bits/stdc++.h>. Provide a minimal shim so
# starter syntax can still be validated locally; Judge0 (Linux g++) has the
# real header, so this only affects the local lint.
BITS_SHIM = """#pragma once
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <unordered_map>
#include <unordered_set>
#include <map>
#include <set>
#include <queue>
#include <stack>
#include <deque>
#include <cmath>
#include <climits>
#include <cctype>
#include <functional>
#include <numeric>
#include <sstream>
#include <iomanip>
#include <list>
#include <utility>
"""


def ensure_bits_shim(tmp):
    bits_dir = tmp / "bits"
    bits_dir.mkdir(exist_ok=True)
    (bits_dir / "stdc++.h").write_text(BITS_SHIM, encoding="utf-8")
    return tmp


def check_cpp(slug, source, tmp, errors):
    if GPP is None:
        return
    cpp_file = tmp / f"{slug.replace('-', '_')}.cpp"
    cpp_file.write_text(source, encoding="utf-8")
    proc = subprocess.run(
        [GPP, "-std=c++17", "-fsyntax-only", f"-I{tmp}", str(cpp_file)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        errors.append(f"[cpp] {slug}:\n{proc.stderr.strip()[:500]}")


def main():
    if JAVAC is None:
        print("WARN: javac not found — skipping Java validation")
    if GPP is None:
        print("WARN: g++ not found — skipping C++ validation")

    errors = []
    checked = 0
    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        ensure_bits_shim(tmp)
        for problem in PROBLEMS:
            slug = problem["slug"]
            starter = problem.get("starter_code") or {}
            if not starter:
                continue  # catalog-only entry, nothing to compile
            checked += 1
            if starter.get("python"):
                check_python(slug, starter["python"], errors)
            if starter.get("java"):
                check_java(slug, starter["java"], tmp, errors)
            if starter.get("cpp"):
                check_cpp(slug, starter["cpp"], tmp, errors)

    if errors:
        print(f"FAILED ({len(errors)} error(s) across {checked} solvable problems):")
        for err in errors:
            print(f"  {err}")
        return 1
    print(f"All starters valid across {checked} solvable problems (py / javac / g++).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
