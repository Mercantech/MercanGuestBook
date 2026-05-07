from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REQUIRED_BULLETS = [
    r"^\s*-\s*\*\*GitHub\*\*:\s*(\S+)\s*$",
    r"^\s*-\s*\*\*Website\*\*:\s*(\S+)\s*$",
    r"^\s*-\s*\*\*Quote\*\*:\s*(.+?)\s*$",
]


@dataclass(frozen=True)
class DiffEntry:
    status: str
    path: str


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT).strip()


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def parse_name_status(output: str) -> list[DiffEntry]:
    entries: list[DiffEntry] = []
    if not output.strip():
        return entries
    for line in output.splitlines():
        # Format: <status>\t<path>
        parts = line.split("\t", 1)
        if len(parts) != 2:
            fail(f"Kan ikke parse git diff-linje: {line!r}")
        status, path = parts[0].strip(), parts[1].strip()
        entries.append(DiffEntry(status=status, path=path))
    return entries


def is_http_url(s: str) -> bool:
    return s.startswith("http://") or s.startswith("https://")


def main() -> int:
    base = os.environ.get("BASE_SHA")
    head = os.environ.get("HEAD_SHA")
    if not base or not head:
        fail("Mangler BASE_SHA og/eller HEAD_SHA environment variables.")

    diff_out = run(["git", "diff", "--name-status", f"{base}..{head}"])
    changed = parse_name_status(diff_out)

    entry_changes = [c for c in changed if c.path.startswith("entries/")]
    allowed_non_entry = {"README.md"}
    non_entry_changes = [c for c in changed if not c.path.startswith("entries/") and c.path not in allowed_non_entry]

    if non_entry_changes:
        fail(
            "PR må kun ændre filer i entries/ (og README.md som genereres automatisk). Uventede ændringer:\n"
            + "\n".join(f"- {c.status} {c.path}" for c in non_entry_changes)
        )

    if not entry_changes:
        fail("PR skal ændre præcis én fil i entries/. (Ingen ændringer fundet.)")

    # Allow add/modify/rename as long as exactly one file ends up in entries/
    # Exclude template file from being changed by students.
    touched_paths = sorted({c.path for c in entry_changes})
    if "entries/_template.md" in touched_paths:
        fail("Du må ikke ændre entries/_template.md. Kopiér den i stedet til din egen fil.")

    if len(touched_paths) != 1:
        fail(
            "PR skal ændre præcis én fil i entries/. Fandt:\n"
            + "\n".join(f"- {p}" for p in touched_paths)
        )

    entry_path = Path(touched_paths[0])
    if entry_path.suffix.lower() != ".md":
        fail("Entry-filen skal være en .md fil.")

    if not entry_path.exists():
        # In workflows, checkout contains HEAD; if renamed/deleted, fail.
        fail(f"Entry-filen findes ikke i head: {entry_path.as_posix()}")

    content = entry_path.read_text(encoding="utf-8", errors="replace")

    missing: list[str] = []
    captures: dict[str, str] = {}
    for i, pat in enumerate(REQUIRED_BULLETS):
        m = re.search(pat, content, flags=re.MULTILINE)
        if not m:
            missing.append(pat)
        else:
            captures[str(i)] = m.group(1).strip()

    if missing:
        fail(
            "Entry-filen mangler obligatoriske linjer (GitHub/Website/Quote) i korrekt format.\n"
            "Brug entries/_template.md som udgangspunkt."
        )

    gh = captures["0"]
    website = captures["1"]

    if not is_http_url(gh):
        fail("GitHub-link skal starte med http:// eller https://")
    if not is_http_url(website):
        fail("Website-link skal starte med http:// eller https://")

    # Soft sanity check for GitHub URL
    if "github.com/" not in gh:
        fail("GitHub-link skal pege på github.com/<handle>.")

    print(f"OK: Validerede {entry_path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

