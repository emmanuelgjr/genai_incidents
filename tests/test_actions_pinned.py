"""D134(ii): every workflow `uses:` is pinned to a full 40-hex commit SHA with a
trailing `# vX...` release comment; dependabot keeps the pins moving.

The check covers `.github/workflows/*.y*ml` and `.github/actions/**/action.y*ml`."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
USES = re.compile(r"^\s*(?:-\s+)?uses:\s*(?P<ref>\S+)(?P<rest>.*)$")
PINNED = re.compile(r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")
COMMENT = re.compile(r"^\s+#\s*v\d")


def check_pins(name: str, text: str) -> list[str]:
    problems = []
    for n, line in enumerate(text.splitlines(), 1):
        m = USES.match(line)
        if not m:
            continue
        ref = m["ref"]
        if ref.startswith("./") or ref.startswith("docker://"):
            continue
        if not PINNED.match(ref):
            problems.append(f"{name}:{n}: not pinned to a 40-hex sha: {ref}")
        elif not COMMENT.match(m["rest"]):
            problems.append(f"{name}:{n}: pinned but no trailing '# vX.Y.Z' comment: {ref}")
    return problems


def workflow_files(root: Path) -> list[Path]:
    gh = root / ".github"
    found = set()
    for ext in ("yml", "yaml"):
        found.update(gh.glob(f"workflows/*.{ext}"))
        found.update(gh.glob(f"actions/**/action.{ext}"))
    return sorted(found)


def check_tree(root: Path) -> list[str]:
    return [
        p
        for f in workflow_files(root)
        for p in check_pins(f.relative_to(root).as_posix(), f.read_text(encoding="utf-8"))
    ]


def test_every_workflow_action_is_sha_pinned_with_version_comment():
    assert workflow_files(ROOT)
    problems = check_tree(ROOT)
    assert not problems, "\n".join(problems)


def test_workflow_file_discovery_covers_yaml_and_composite_actions(tmp_path):
    names = [
        ".github/workflows/a.yml",
        ".github/workflows/b.yaml",
        ".github/actions/x/action.yml",
        ".github/actions/y/z/action.yaml",
    ]
    for n in names + [".github/workflows/readme.md"]:
        f = tmp_path / n
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("# nothing\n", encoding="utf-8")
    assert [f.relative_to(tmp_path).as_posix() for f in workflow_files(tmp_path)] == sorted(names)
    assert check_tree(tmp_path) == []
    bad = "      - uses: actions/checkout@v6\n"
    (tmp_path / ".github/workflows/b.yaml").write_text(bad, encoding="utf-8")
    (tmp_path / ".github/actions/x/action.yml").write_text(bad, encoding="utf-8")
    problems = check_tree(tmp_path)
    assert any(p.startswith(".github/workflows/b.yaml:") for p in problems)
    assert any(p.startswith(".github/actions/x/action.yml:") for p in problems)


def test_pin_check_fires():
    good = "      - uses: actions/checkout@" + "a" * 40 + " # v6.1.0\n"
    assert check_pins("w", good) == []
    assert check_pins("w", good.replace("a" * 40 + " # v6.1.0", "v6")), "tag ref must fail"
    assert check_pins("w", good.replace("a" * 40, "a" * 39)), "39-hex must fail"
    assert check_pins("w", good.replace(" # v6.1.0", "")), "missing comment must fail"
    assert check_pins("w", good.replace("# v6.1.0", "# latest")), "non-version comment must fail"
    assert check_pins("w", good.replace("a" * 40, "A" * 40)), "uppercase/non-hex must fail"
    assert check_pins("w", "    uses: x/y@" + "a" * 40 + "\n"), "bare key form must be checked"
    assert check_pins("w", "      - uses: ./local\n      - uses: docker://alpine:3\n") == []


def test_dependabot_covers_github_actions():
    cfg = yaml.safe_load((ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8"))
    assert cfg["version"] == 2
    gh = [u for u in cfg["updates"] if u["package-ecosystem"] == "github-actions"]
    assert gh and gh[0]["directory"] == "/" and gh[0]["schedule"]["interval"] == "weekly"
