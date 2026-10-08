#!/usr/bin/env bash
# Draft the next release's version bump, changelog entry, and GitHub release
# notes from git history with `claude -p`. Nothing in the repository is changed:
# review the generated file and apply it by hand.
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: scripts/release-notes.sh [--from REF] [--to REF] [--out DIR] [--model NAME] [--dry-run]

  --from REF     Start of the range (default: latest tag, or the root commit).
  --to REF       End of the range (default: HEAD).
  --out DIR      Output directory (default: .release).
  --model NAME   Claude model passed to `claude --model`.
  --dry-run      Write the context and prompt files without calling Claude.

Writes DIR/context.md, DIR/prompt.md, and DIR/release.md.
EOF
}

die() {
    echo "release-notes: $*" >&2
    exit 1
}

readonly DIFF_LINE_LIMIT=1500
readonly REQUIRED_HEADINGS=("## Version" "## Changelog" "## Release notes")

from=""
to="HEAD"
out=".release"
model=""
dry_run=false

while (($#)); do
    case "$1" in
        --from) from="${2:?--from needs a ref}"; shift 2 ;;
        --to) to="${2:?--to needs a ref}"; shift 2 ;;
        --out) out="${2:?--out needs a directory}"; shift 2 ;;
        --model) model="${2:?--model needs a name}"; shift 2 ;;
        --dry-run) dry_run=true; shift ;;
        -h | --help) usage; exit 0 ;;
        *) usage >&2; die "unknown argument: $1" ;;
    esac
done

root="$(git rev-parse --show-toplevel 2>/dev/null)" || die "run this inside the git repository"
cd "$root"

if [[ -z "$from" ]]; then
    from="$(git describe --tags --abbrev=0 "$to" 2>/dev/null)" \
        || from="$(git rev-list --max-parents=0 "$to" | tail -n 1)"
fi
git rev-parse --verify --quiet "$from^{commit}" >/dev/null || die "unknown ref: $from"
git rev-parse --verify --quiet "$to^{commit}" >/dev/null || die "unknown ref: $to"

range="$from..$to"
commit_count="$(git rev-list --count --no-merges "$range")"
((commit_count > 0)) || die "no commits in range $range"

if ! $dry_run; then
    command -v claude >/dev/null || die "claude is not on PATH (use --dry-run to skip it)"
fi

version="$(uv version --short 2>/dev/null || sed -n 's/^version = "\(.*\)"/\1/p' pyproject.toml)"
repo_url="https://github.com/difegam/django-daisy-forms"

# Read CHANGELOG.md as of the end of the range. For HEAD, use the working tree
# so uncommitted Unreleased entries are included.
if [[ "$(git rev-parse "$to^{commit}")" == "$(git rev-parse HEAD)" ]]; then
    changelog="$(cat CHANGELOG.md)"
else
    changelog="$(git show "$to:CHANGELOG.md" 2>/dev/null || true)"
fi

# Print a CHANGELOG section body: everything under the first heading that
# starts with $1, up to the next version heading or the link references.
changelog_section() {
    awk -v heading="$1" '
        index($0, heading) == 1 { found = 1; next }
        found && /^## \[/ { exit }
        found && /^\[[^]]+\]: / { exit }
        found { print }
    ' <<<"$changelog"
}

mkdir -p "$out"
context="$out/context.md"
prompt="$out/prompt.md"
result="$out/release.md"

{
    echo "# Release context for django-daisy-forms"
    echo
    echo "- Repository: $repo_url"
    echo "- Current package version: $version"
    echo "- Range: $range ($commit_count commits, merges excluded)"
    echo
    echo "## Commits"
    echo
    git log --no-merges --reverse --format='### %h %s%n%nAuthor: %an, %as%n%n%b' "$range"
    echo
    echo "## Diff summary"
    echo
    echo '```text'
    git diff --stat=120 "$range"
    echo '```'
    echo
    echo "## Package diff (src/ and pyproject.toml)"
    echo
    echo '```diff'
    git diff "$range" -- src pyproject.toml >"$out/package.diff"
    head -n "$DIFF_LINE_LIMIT" "$out/package.diff"
    if (($(wc -l <"$out/package.diff") > DIFF_LINE_LIMIT)); then
        echo "... diff truncated after $DIFF_LINE_LIMIT lines ..."
    fi
    echo '```'
    echo
    echo "## Other changed files"
    echo
    for area in tests .github docs README.md CHANGELOG.md justfile; do
        files="$(git diff --name-only "$range" -- "$area")"
        if [[ -n "$files" ]]; then
            printf -- '- %s\n' "$area"
            while IFS= read -r file; do
                printf -- '  - %s\n' "$file"
            done <<<"$files"
        fi
    done
    echo
    echo "## CHANGELOG.md at $to: Unreleased section"
    echo
    changelog_section "## [Unreleased]"
    echo
    echo "## CHANGELOG.md at $to: latest released section (style reference)"
    echo
    latest="$(grep -m 1 -E '^## \[[0-9]' <<<"$changelog" || true)"
    if [[ -n "$latest" ]]; then
        echo "$latest"
        changelog_section "$latest"
    fi
} >"$context"
rm -f "$out/package.diff"

cat >"$prompt" <<EOF
You are the release manager for django-daisy-forms, a Django package that
renders daisyUI 5 form markup. Its public surface is the form renderer, the
{% daisy_field %} template tag and its options, the widgets, the templates and
their CSS classes, the daisy_forms_css management command, and the system
checks. The release context (git history since $from, diffs, and the current
CHANGELOG.md sections) is provided on standard input.

Write exactly these three sections in Markdown, in this order, with no text
before the first heading:

## Version
The semver bump (patch, minor, or major) from the current version $version and
the resulting version number, followed by a one-sentence reason. The package is
pre-1.0: a breaking change is a minor bump, and anything else is a patch bump.

## Changelog
Entries for CHANGELOG.md in Keep a Changelog format under ### Added,
### Changed, ### Deprecated, ### Removed, ### Fixed, or ### Security, omitting
empty groups. Match the style of the latest released section. List only
changes a package user would notice; leave out internal refactors, tests, CI,
and development tooling unless they change what users install or run. Merge
with the current Unreleased entries without duplicating them. Do not include a
version heading.

## Release notes
GitHub release notes: a one-paragraph summary, a short list of highlights, an
"Upgrading" subsection only when users must act (for example, regenerating the
daisy_forms_css output), and links to the pull requests mentioned in commit
subjects as $repo_url/pull/<number>.

Use only facts from the provided context. Do not invent changes, issue
numbers, or contributors. If the range has no user-facing changes, say so in
each section.
EOF

echo "Context: $context"
echo "Prompt:  $prompt"

if $dry_run; then
    echo "Dry run: skipped claude."
    exit 0
fi

echo "Asking Claude to draft release notes for $range ($commit_count commits)..."
claude_args=(-p "$(<"$prompt")" --output-format text --no-session-persistence)
if [[ -n "$model" ]]; then
    claude_args+=(--model "$model")
fi
# --tools takes a variadic list, so it stays last; "" disables every tool.
claude_args+=(--tools "")
claude "${claude_args[@]}" <"$context" >"$result"

[[ -s "$result" ]] || die "claude returned no output"
for heading in "${REQUIRED_HEADINGS[@]}"; do
    grep -qx "$heading" "$result" || die "output is missing '$heading'; see $result"
done

echo "Release draft: $result"
echo
awk '/^## Version$/ { found = 1 } found && /^## Changelog$/ { exit } found' "$result"
