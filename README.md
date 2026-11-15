# adf-parse

Convert [Atlassian Document Format (ADF)](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/) — the JSON format used by Jira and Confluence — into plain text / Markdown.

Zero dependencies. Supports paragraphs, headings, bullet/ordered lists (with nesting), code blocks, tables (with header detection), blockquotes, panels, expands, task lists, mentions, emoji, dates, statuses, inline cards, hard breaks, rules, and media references. Inline marks render as real Markdown: links `[text](url)`, **bold**, *italic*, ~~strikethrough~~, and `code`.

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
#
# [See the docs](https://example.com)
```

For search indexes, RAG, and LLM/agent pipelines, use plain mode — it drops emoji and all Markdown decoration (`**`, `*`, `~~`, backticks, `[text](url)`), giving clean text while links and media are still collected as data:

```python
from adf_parse import create_text_doc

create_text_doc(adf)          # clean plain text
parse_doc(adf, plain=True)    # same, with .links and .media_ref
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
