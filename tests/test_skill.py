import re
import tomllib
from pathlib import Path

import pytest

SKILL_DIR = Path("skills/django-daisy-forms")
SKILL = SKILL_DIR / "SKILL.md"


def _package_version() -> str:
    configuration = tomllib.loads(Path("pyproject.toml").read_text())
    return str(configuration["project"]["version"])


def _frontmatter() -> str:
    match = re.match(r"^---\n(.*?)\n---\n", SKILL.read_text(), re.DOTALL)
    assert match, f"{SKILL} has no YAML frontmatter"
    return match.group(1)


def test_skill_metadata_version_matches_package() -> None:
    match = re.search(r'(?m)^metadata:\n  version: "([^"]+)"$', _frontmatter())

    assert match, "SKILL.md frontmatter needs metadata.version"
    assert match.group(1) == _package_version(), (
        "Skill version differs from the package; run `just skill-refresh` "
        "and give the printed prompt to your agent"
    )


def test_skill_body_version_matches_package() -> None:
    pattern = r"describes django-daisy-forms \*\*([^*]+)\*\*"
    match = re.search(pattern, SKILL.read_text())

    assert match, "SKILL.md body must state the version it describes"
    assert match.group(1) == _package_version(), (
        "Skill version differs from the package; run `just skill-refresh` "
        "and give the printed prompt to your agent"
    )


def test_skill_frontmatter_follows_agent_skills_spec() -> None:
    frontmatter = _frontmatter()
    name = re.search(r"(?m)^name: (.+)$", frontmatter)
    description = re.search(r"(?ms)^description: >-\n(.*?)\n(?=\S)", frontmatter)

    assert name and name.group(1) == SKILL_DIR.name
    assert description
    assert len(" ".join(description.group(1).split())) <= 1024
    assert re.search(r'(?m)^argument-hint: "\[', frontmatter)


def test_skill_reference_links_resolve() -> None:
    for page in (SKILL, *SKILL_DIR.glob("references/*.md")):
        for target in re.findall(r"\]\((?!https?:)([^)#]+\.md)", page.read_text()):
            assert (page.parent / target).is_file(), f"{page}: broken link {target}"


@pytest.mark.parametrize("part", ["patch", "minor", "major"], ids=str)
def test_bump_recipe_asks_for_a_skill_refresh(part: str) -> None:
    justfile = Path("justfile").read_text()
    recipe = justfile.split(f"bump-{part}:", 1)[1].split("\n\n", 1)[0]

    assert "just skill-refresh" in recipe
    assert "sync-skill-version" not in recipe


def test_skill_refresh_recipe_and_hook_print_the_prompt() -> None:
    justfile = Path("justfile").read_text()
    hooks = Path(".pre-commit-config.yaml").read_text()
    recipe = justfile.split("skill-refresh:", 1)[1].split("\n\n", 1)[0]

    assert "scripts/skill-refresh-prompt.sh" in recipe
    assert "entry: scripts/skill-refresh-prompt.sh" in hooks
