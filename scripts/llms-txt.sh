#!/usr/bin/env bash
# Generate llms.txt (https://llmstxt.org/) for the documentation site from the
# `nav` in zensical.toml, and copy each page's markdown source next to it so
# every link in the file resolves to clean markdown on the same site.
# Run it after `zensical build`: a `--clean` build wipes the output directory.
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: scripts/llms-txt.sh [--out FILE] [--check]

  --out FILE   Output file (default: site/llms.txt). Page markdown is copied
               into the same directory.
  --check      Do not write anything; exit 1 if FILE is missing or out of date.

Reads site metadata and the nav from zensical.toml and page descriptions from
the first paragraph of each page under docs_dir.
EOF
}

die() {
    echo "llms-txt: $*" >&2
    exit 1
}

readonly CONFIG="zensical.toml"
# Nav groups (or top-level pages) listed under the spec's "Optional" section.
readonly OPTIONAL_GROUPS=("Development" "Changelog")
readonly DESCRIPTION_LIMIT=200

out="site/llms.txt"
check=false

while (($#)); do
    case "$1" in
        -o | --out) out="${2:?--out needs a file}"; shift 2 ;;
        --check) check=true; shift ;;
        -h | --help) usage; exit 0 ;;
        *) usage >&2; die "unknown argument: $1" ;;
    esac
done

root="$(git rev-parse --show-toplevel)" || die "not inside a git repository"
cd "$root"
[[ -f "$CONFIG" ]] || die "$CONFIG not found"

# Read a top-level string setting from the [project] table.
setting() {
    sed -n "/^\[project\]/,/^\[/{s/^$1 *= *\"\(.*\)\"/\1/p;}" "$CONFIG" | head -n 1
}

# Print the nav as "group<TAB>title<TAB>path" lines. Top-level pages use their
# own title as the group.
nav_entries() {
    awk '
        /^nav = \[/ { in_nav = 1; next }
        in_nav && /^\]/ { exit }
        !in_nav { next }
        /^    \{ .* = \[/ {
            group = $0
            sub(/^    \{ "?/, "", group)
            sub(/"? = \[.*/, "", group)
            next
        }
        /^        \{ .* = ".*" \}/ {
            line = $0
            sub(/^        \{ "?/, "", line)
            title = line; sub(/"? = ".*/, "", title)
            path = line; sub(/^.*= "/, "", path); sub(/".*/, "", path)
            print group "\t" title "\t" path
            next
        }
        /^    \{ .* = ".*" \}/ {
            line = $0
            sub(/^    \{ "?/, "", line)
            title = line; sub(/"? = ".*/, "", title)
            path = line; sub(/^.*= "/, "", path); sub(/".*/, "", path)
            print title "\t" title "\t" path
        }
    ' "$CONFIG"
}

# First sentence of a page's first plain paragraph, with markdown links
# flattened and attribute lists dropped. Prints nothing when there is none.
page_description() {
    awk -v limit="$DESCRIPTION_LIMIT" '
        NR == 1 && /^---$/ { front = 1; next }
        front { if (/^---$/) front = 0; next }
        /^```/ { fence = !fence; next }
        fence { next }
        /^[[:space:]]*$/ { if (para != "") exit; next }
        para == "" && /^([#<!?|>*:{+-]|[0-9]+\.|--8<--|[[:space:]])/ { next }
        { para = (para == "" ? $0 : para " " $0) }
        END {
            gsub(/\[([^]]*)\]\([^)]*\)/, "&", para)
            while (match(para, /\[[^]]*\]\([^)]*\)/)) {
                text = substr(para, RSTART + 1, index(substr(para, RSTART), "]") - 2)
                para = substr(para, 1, RSTART - 1) text substr(para, RSTART + RLENGTH)
            }
            gsub(/ ?\{[:.#][^}]*\}/, "", para)
            gsub(/\*\*/, "", para)
            if (match(para, /[.!?]( |$)/)) para = substr(para, 1, RSTART)
            if (length(para) > limit) para = substr(para, 1, limit - 1) "…"
            print para
        }
    ' "$1"
}

is_optional() {
    local group
    for group in "${OPTIONAL_GROUPS[@]}"; do
        [[ "$1" == "$group" ]] && return 0
    done
    return 1
}

site_name="$(setting site_name)"
site_description="$(setting site_description)"
site_url="$(setting site_url)"
docs_dir="$(setting docs_dir)"
[[ -n "$site_name" && -n "$site_url" && -n "$docs_dir" ]] || die "site_name, site_url and docs_dir must be set in $CONFIG"
site_url="${site_url%/}/"

entries="$(nav_entries)"
[[ -n "$entries" ]] || die "no nav entries found in $CONFIG"

# Resolve a nav path to the markdown file that holds its real content.
source_for() {
    if [[ "$1" == "changelog.md" ]]; then echo "CHANGELOG.md"; else echo "$docs_dir/$1"; fi
}

# Print the link list for the main (optional=false) or Optional sections.
emit_sections() {
    local want_optional="$1" previous="" group title path source description
    while IFS=$'\t' read -r group title path; do
        [[ "$group" == "Home" ]] && continue
        if is_optional "$group"; then [[ "$want_optional" == true ]] || continue
        else [[ "$want_optional" == false ]] || continue; fi
        source="$(source_for "$path")"
        [[ -f "$source" ]] || die "nav page not found: $source"
        description="$(page_description "$source")"
        # Card-grid overview pages have no prose of their own.
        [[ "$title" == "Overview" && -z "$description" ]] && continue
        if [[ "$want_optional" == false && "$group" != "$previous" ]]; then
            [[ -n "$previous" ]] && echo
            echo "## $group"
            echo
            previous="$group"
        fi
        if [[ "$want_optional" == true && -z "$previous" ]]; then
            echo "## Optional"
            echo
            previous="optional"
        fi
        if [[ "$want_optional" == true && "$title" == "Overview" ]]; then title="$group overview"; fi
        echo "- [$title](${site_url}${path})${description:+: $description}"
    done <<<"$entries"
}

generate() {
    echo "# $site_name"
    echo
    echo "> $site_description"
    echo
    echo "Documentation for django-daisy-forms, a Django package. Each link below"
    echo "points to the markdown source of a documentation page."
    echo
    emit_sections false
    echo
    emit_sections true
}

content="$(generate)"

if [[ "$check" == true ]]; then
    [[ -f "$out" ]] || die "$out is missing"
    [[ "$content" == "$(<"$out")" ]] || die "$out is out of date"
    echo "llms-txt: $out is up to date"
    exit 0
fi

out_dir="$(dirname "$out")"
mkdir -p "$out_dir"
while IFS=$'\t' read -r group _ path; do
    [[ "$group" == "Home" ]] && continue
    mkdir -p "$out_dir/$(dirname "$path")"
    cp "$(source_for "$path")" "$out_dir/$path"
done <<<"$entries"
printf '%s\n' "$content" >"$out"
echo "llms-txt: wrote $out ($(grep -c '^- \[' "$out") links)"
