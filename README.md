# adf-parse

Convert [Atlassian Document Format (ADF)](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/) — the JSON format used by Jira and Confluence — into plain text / Markdown.

Zero dependencies. Supports paragraphs, headings, bullet/ordered lists (with nesting), code blocks, tables (with header detection), blockquotes, panels, expands, task lists, mentions, dates, statuses, inline cards, hard breaks, rules, and media references.

## Installation

```bash
pip install adf-parse
```

Requires Python 3.11+.

## Usage

```python
from adf_parse import create_md_doc, parse_doc

adf = {
    "type": "doc",
    "version": 1,
    "content": [
        {"type": "heading", "attrs": {"level": 2},
         "content": [{"type": "text", "text": "Release notes"}]},
        {"type": "paragraph",
         "content": [{"type": "text", "text": "See the docs",
                      "marks": [{"type": "link", "attrs": {"href": "https://example.com"}}]}]},
    ],
}

print(create_md_doc(adf))
# ## Release notes
# See the docs (https://example.com)
```

To also get the extracted links and media references, use `parse_doc`:

```python
result = parse_doc(adf)
result.collected_text  # list of rendered blocks
result.links           # list of (text, href) tuples
result.media_ref       # list of MediaRef(ref_type, ref)
```

## License

MIT
