#!/usr/bin/env bash
# Check that the agent skill matches the package version. On a mismatch, print a
# prompt that asks a coding agent to update the skill from the git history, and
# exit 1. Used by `just skill-refresh` and the skill-version pre-commit hook.
set -euo pipefail

cd "$(dirname "$0")/.."

skill="skills/django-daisy-forms/SKILL.md"
package_version="$(uv version --short)"
skill_version="$(sed -n 's/^  version: "\(.*\)"$/\1/p' "$skill" | head -n 1)"

if [[ -z "$skill_version" ]]; then
  echo "$skill has no metadata.version." >&2
  exit 1
fi

if [[ "$skill_version" == "$package_version" ]]; then
  echo "Agent skill is up to date ($skill_version)."
  exit 0
fi

# The skill was last reviewed in the commit that set its version line.
base="$(git log -1 --format=%h -G '^  version: ' -- "$skill")"
if [[ -z "$base" ]] && git rev-parse -q --verify "refs/tags/v$skill_version" >/dev/null; then
  base="v$skill_version"
fi
if [[ -z "$base" ]]; then
  echo "Cannot find the commit or tag for skill version $skill_version." >&2
  exit 1
fi

cat <<EOF
The agent skill ($skill_version) does not match the package ($package_version).
Paste this prompt into your coding agent (Claude Code, Codex, ...), review the
skill diff it produces, and commit it together with the version bump.

----- prompt -----
Update the django-daisy-forms agent skill from $skill_version to $package_version.

1. Read what changed since the skill was last updated ($base):
   git log --oneline $base..HEAD -- src/ docs/ CHANGELOG.md
   git diff $base..HEAD -- src/daisy_forms docs CHANGELOG.md
   Include uncommitted changes too (git diff HEAD -- src/daisy_forms docs CHANGELOG.md).
2. Read $skill and every file in skills/django-daisy-forms/references/.
3. Update only what the changes affect: settings, template tag options, widgets,
   management command flags, system checks, error messages, Tailwind or daisyUI
   requirements, and htmx guidance. Verify every claim against src/daisy_forms;
   the code wins over the docs. Keep the existing structure and style.
4. Run scripts/sync-skill-version.sh to set the skill version to $package_version.
5. Run: uv run pytest -q tests/test_skill.py && uv run ruff format --check skills
6. Summarise what you changed in the skill and why, citing the commits.
----- end prompt -----

Commits since $base:
EOF
git log --oneline "$base..HEAD" -- src/ docs/ CHANGELOG.md
exit 1
