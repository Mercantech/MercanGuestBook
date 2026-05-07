from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


INDEX_START = "<!-- GUESTBOOK_INDEX_START -->"
INDEX_END = "<!-- GUESTBOOK_INDEX_END -->"


@dataclass(frozen=True)
class Entry:
    handle: str
    path: Path
    github_url: str
    website_url: str
    quote: str
    created_ts: int


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT).strip()


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)


def parse_entry_md(path: Path) -> tuple[str, str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    gh = re.search(r"^\s*-\s*\*\*GitHub\*\*:\s*(\S+)\s*$", text, flags=re.MULTILINE)
    web = re.search(r"^\s*-\s*\*\*Website\*\*:\s*(\S+)\s*$", text, flags=re.MULTILINE)
    quote = re.search(r'^\s*-\s*\*\*Quote\*\*:\s*"?(.+?)"?\s*$', text, flags=re.MULTILINE)
    if not gh or not web or not quote:
        fail(f"Mangler GitHub/Website/Quote i {path.as_posix()}")
    return gh.group(1).strip(), web.group(1).strip(), quote.group(1).strip()


def first_commit_ts_for_file(path: Path) -> int:
    # Find timestamp for the commit where the file was first added.
    out = run(["git", "log", "--diff-filter=A", "--follow", "--format=%ct", "--", path.as_posix()])
    if not out:
        # Fallback: if file is uncommitted yet, use a large number so it ends bottom in local generation.
        return 2_147_483_647
    # git log returns newest->oldest; the *first add* will typically be last line
    lines = [ln.strip() for ln in out.splitlines() if ln.strip().isdigit()]
    if not lines:
        return 2_147_483_647
    return int(lines[-1])


def build_index(entries: list[Entry]) -> str:
    lines: list[str] = []
    lines.append("| # | Handle | Quote | Links |")
    lines.append("|---:|---|---|---|")
    for i, e in enumerate(entries, start=1):
        links = f"[GitHub]({e.github_url}) · [Website]({e.website_url}) · [Fil]({e.path.as_posix()})"
        lines.append(f"| {i} | `{e.handle}` | {e.quote} | {links} |")
    lines.append("")
    return "\n".join(lines)


def inject_index(base_text: str, index_md: str) -> str:
    if INDEX_START not in base_text or INDEX_END not in base_text:
        fail(f"README.base.md skal indeholde både {INDEX_START} og {INDEX_END}")
    pre, rest = base_text.split(INDEX_START, 1)
    _, post = rest.split(INDEX_END, 1)
    # Keep the markers, replace the content between.
    return pre + INDEX_START + "\n\n" + index_md.strip() + "\n\n" + INDEX_END + post


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="Fail hvis README.md ikke matcher genereret output.")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    base_path = repo_root / "README.base.md"
    out_path = repo_root / "README.md"
    entries_dir = repo_root / "entries"

    if not base_path.exists():
        fail("Mangler README.base.md")
    if not entries_dir.exists():
        fail("Mangler entries/ mappe")

    entries: list[Entry] = []
    for p in sorted(entries_dir.glob("*.md")):
        if p.name == "_template.md":
            continue
        handle = p.stem
        gh, web, quote = parse_entry_md(p)
        created_ts = first_commit_ts_for_file(p)
        entries.append(
            Entry(
                handle=handle,
                path=Path("entries") / p.name,
                github_url=gh,
                website_url=web,
                quote=quote,
                created_ts=created_ts,
            )
        )

    # Earlier commit -> higher on the page
    entries.sort(key=lambda e: (e.created_ts, e.handle.lower()))

    base_text = base_path.read_text(encoding="utf-8", errors="replace")
    index_md = build_index(entries)
    generated = "# MercanGuestBook\n\n" + inject_index(base_text, index_md).lstrip()

    if args.check:
        current = out_path.read_text(encoding="utf-8", errors="replace") if out_path.exists() else ""
        if current != generated:
            fail("README.md er ikke opdateret. Kør scripts/generate_readme.py")
        print("OK: README.md matcher genereret output")
        return 0

    out_path.write_text(generated, encoding="utf-8")
    print("OK: Genererede README.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

