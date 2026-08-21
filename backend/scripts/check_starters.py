import asyncio
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import httpx

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.seeds import PROBLEMS

JUDGE0_URL = "http://localhost:2358/submissions?base64_encoded=false&wait=true&fields=status_id"
JAVAC = Path(r"C:\Program Files\Eclipse Adoptium\jdk-21.0.11.10-hotspot\bin\javac.exe")
CPP_LANGUAGE_ID = 54
CHUNK = 8


def check_python(slug, source, errors):
    try:
        compile(source, f"{slug}.py", "exec")
    except SyntaxError as exc:
        errors.append(f"[py] {slug}: {exc}")


def check_java(slug, source, tmp, errors):
    problem_dir = tmp / slug.replace("-", "_")
    problem_dir.mkdir(parents=True, exist_ok=True)
    java_file = problem_dir / "Main.java"
    java_file.write_text(source, encoding="utf-8")
    proc = subprocess.run(
        [str(JAVAC), "-d", str(problem_dir), str(java_file)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        errors.append(f"[java] {slug}:\n{proc.stderr.strip()[:500]}")
    else:
        shutil.rmtree(problem_dir, ignore_errors=True)


async def check_cpp(client, slug, source, sem, errors):
    async with sem:
        try:
            resp = await client.post(
                JUDGE0_URL,
                json={"language_id": CPP_LANGUAGE_ID, "source_code": source, "stdin": ""},
                timeout=30,
            )
            resp.raise_for_status()
            status_id = resp.json()["status_id"]
            if status_id == 2:
                errors.append(f"[cpp] {slug}: COMPILATION_ERROR")
        except Exception as exc:
            errors.append(f"[cpp] {slug}: judge0 failed ({exc})")


async def main():
    if not JAVAC.exists():
        print(f"javac not found at {JAVAC}")
        return 1

    errors = []
    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        sem = asyncio.Semaphore(CHUNK)
        async with httpx.AsyncClient() as client:
            for problem in PROBLEMS:
                slug = problem["slug"]
                starter = problem["starter_code"]
                check_python(slug, starter["python"], errors)
                check_java(slug, starter["java"], tmp, errors)
                await check_cpp(client, slug, starter["cpp"], sem, errors)

    total = len(PROBLEMS)
    if errors:
        print(f"FAILED ({len(errors)} error(s) across {total} problems):")
        for err in errors:
            print(f"  {err}")
        return 1
    print(f"All starters valid across {total} problems (py compile / javac / judge0 g++).")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
