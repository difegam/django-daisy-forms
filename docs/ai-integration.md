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
