"""D134(ii): every workflow `uses:` is pinned to a full 40-hex commit SHA with a
trailing `# vX...` release comment; dependabot keeps the pins moving."""

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


def test_every_workflow_action_is_sha_pinned_with_version_comment():
    files = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    assert files
    problems = [p for f in files for p in check_pins(f.name, f.read_text(encoding="utf-8"))]
    assert not problems, "\n".join(problems)


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
