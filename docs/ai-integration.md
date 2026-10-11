# AI Integration

These docs are readable by AI assistants: a machine-friendly index at `/llms.txt` and a plain Markdown copy of every page.

## llms.txt

The site publishes an [llms.txt](https://llmstxt.org/) file, a short Markdown index that tells an assistant what the project is and where each page lives:

<https://difegam.github.io/django-daisy-forms/llms.txt>

It contains:

- The project name and a one-line summary.
- Every documentation page, grouped like the site menu, each with a link to its Markdown source and a short description.
- An `## Optional` section for secondary pages (development notes and the changelog) that an assistant can skip when it needs less context.

The file is generated from the site navigation by `scripts/llms-txt.sh` on every deploy, so it always matches the published docs.

## Markdown for every page

Each page has a plain Markdown copy next to it. Replace the trailing slash of the page URL with `.md`:

| Page                           | Markdown                         |
| ------------------------------ | -------------------------------- |
| `.../guide/rendering/`         | `.../guide/rendering.md`         |
| `.../reference/template-tags/` | `.../reference/template-tags.md` |

```bash
curl https://difegam.github.io/django-daisy-forms/guide/rendering.md
```

## Use it with an assistant

Point your tool at the index and ask your question. Most assistants can fetch a URL:

```text
Read https://difegam.github.io/django-daisy-forms/llms.txt and show me how to
render a Django form with daisyUI using django-daisy-forms.
```

In Claude Code, Cursor, or any agent with web access, add the URL to your project instructions so the assistant looks up the current docs before it writes form code:

```markdown
For django-daisy-forms, read https://difegam.github.io/django-daisy-forms/llms.txt
```

To give an assistant one page only, such as the [template tag reference](reference/template-tags.md), paste or fetch that page's `.md` URL.

## Agent skill

The repository ships an [Agent Skill](https://agentskills.io/) that teaches coding
agents to set up and use the package. It works with Claude Code, Codex, and other
agents that the [`skills` CLI](https://github.com/vercel-labs/skills) supports:

```bash
npx skills add difegam/django-daisy-forms
```

Add `-a claude-code` or `-a codex` to pick an agent, and `-g` to install it for every
project. The agent loads the skill when it works on Django forms. You can also call it
with a mode and an optional path:

| Command                               | What it does                                                   |
| ------------------------------------- | -------------------------------------------------------------- |
| `/django-daisy-forms setup`           | Installs and configures the package, then wires Tailwind       |
| `/django-daisy-forms form <template>` | Writes or edits forms and templates with `{% daisy_field %}`   |
| `/django-daisy-forms tailwind`        | Generates the CSS source file and adds the CI check            |
| `/django-daisy-forms htmx <view>`     | Adds server-side validation with htmx, per field or whole form |
| `/django-daisy-forms review <path>`   | Audits templates, forms, and settings for common mistakes      |

The skill lives in `skills/django-daisy-forms` in the [repository](https://github.com/difegam/django-daisy-forms).
The skill's version always matches the package release it documents. It is set in
`metadata.version` and in the skill text. On every release, the maintainers update the skill
from the git history since its previous version, and a pre-commit hook blocks a
version bump that skips this step. Before writing code, the agent compares it
with the installed package. If the package is newer, the agent reads the changelog and
`llms.txt` and suggests `npx skills update django-daisy-forms`. If the package is
older, the agent checks the changelog before it uses newer features.
