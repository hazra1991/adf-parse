from adf_parse import create_md_doc, parse_doc
from adf_parse.enums import MediaRefType


def doc(*content):
    return {"type": "doc", "version": 1, "content": list(content)}


def text(value, *marks):
    node = {"type": "text", "text": value}
    if marks:
        node["marks"] = list(marks)
    return node


def para(*content):
    return {"type": "paragraph", "content": list(content)}


def test_heading():
    assert create_md_doc(doc(
        {"type": "heading", "attrs": {"level": 3}, "content": [text("Title")]}
    )) == "### Title"


def test_plain_paragraph():
    assert create_md_doc(doc(para(text("hello world")))) == "hello world"


def test_paragraphs_separated_by_blank_line():
    out = create_md_doc(doc(para(text("one")), para(text("two"))))
    assert out == "one\n\ntwo"


def test_link_renders_markdown_and_is_collected():
    adf = doc(para(text("docs", {"type": "link", "attrs": {"href": "https://x.io"}})))
    assert create_md_doc(adf) == "[docs](https://x.io)"
    assert parse_doc(adf).links == [("docs", "https://x.io")]


def test_code_mark():
    assert create_md_doc(doc(para(text("x = 1", {"type": "code"})))) == "`x = 1`"


def test_strong_em_strike_marks():
    adf = doc(para(
        text("bold", {"type": "strong"}),
        text(" and "),
        text("italic", {"type": "em"}),
        text(" and "),
        text("gone", {"type": "strike"}),
    ))
    assert create_md_doc(adf) == "**bold** and *italic* and ~~gone~~"


def test_strong_link_combination_nests_link_outermost():
    adf = doc(para(text(
        "docs",
        {"type": "strong"},
        {"type": "link", "attrs": {"href": "https://x.io"}},
    )))
    assert create_md_doc(adf) == "[**docs**](https://x.io)"


def test_emoji():
    adf = doc(para(
        text("Login fails "),
        {"type": "emoji", "attrs": {"shortName": ":fire:", "text": "🔥"}},
    ))
    assert create_md_doc(adf) == "Login fails 🔥"


def test_emoji_falls_back_to_shortname():
    adf = doc(para({"type": "emoji", "attrs": {"shortName": ":tada:"}}))
    assert create_md_doc(adf) == ":tada:"


def test_bullet_list():
    adf = doc({"type": "bulletList", "content": [
        {"type": "listItem", "content": [para(text("a"))]},
        {"type": "listItem", "content": [para(text("b"))]},
    ]})
    assert create_md_doc(adf) == "- a\n- b"


def test_ordered_list_respects_start():
    adf = doc({"type": "orderedList", "attrs": {"order": 3}, "content": [
        {"type": "listItem", "content": [para(text("a"))]},
        {"type": "listItem", "content": [para(text("b"))]},
    ]})
    assert create_md_doc(adf) == "3. a\n4. b"


def test_nested_bullet_list_is_indented():
    adf = doc({"type": "bulletList", "content": [
        {"type": "listItem", "content": [
            para(text("outer")),
            {"type": "bulletList", "content": [
                {"type": "listItem", "content": [para(text("inner"))]},
            ]},
        ]},
    ]})
    assert create_md_doc(adf) == "- outer\n  - inner"


def test_code_block_with_language():
    adf = doc({"type": "codeBlock", "attrs": {"language": "python"},
               "content": [text("print(1)")]})
    assert create_md_doc(adf) == "```python\nprint(1)\n```"


def test_blockquote():
    adf = doc({"type": "blockquote", "content": [para(text("quoted"))]})
    assert create_md_doc(adf) == "> quoted"


def test_table_with_header_row():
    def cell(kind, value):
        return {"type": kind, "content": [para(text(value))]}

    adf = doc({"type": "table", "content": [
        {"type": "tableRow", "content": [cell("tableHeader", "H1"), cell("tableHeader", "H2")]},
        {"type": "tableRow", "content": [cell("tableCell", "a"), cell("tableCell", "b")]},
    ]})
    assert create_md_doc(adf) == "| H1 | H2 |\n| --- | --- |\n| a | b |"


def test_task_list():
    adf = doc({"type": "taskList", "content": [
        {"type": "taskItem", "attrs": {"state": "DONE"}, "content": [text("done")]},
        {"type": "taskItem", "attrs": {"state": "TODO"}, "content": [text("todo")]},
    ]})
    assert create_md_doc(adf) == "- [x] done\n- [ ] todo"


def test_mention_hard_break_and_rule():
    adf = doc(
        para(text("hi "), {"type": "mention", "attrs": {"text": "@Ana"}},
             {"type": "hardBreak"}, text("next")),
        {"type": "rule"},
    )
    assert create_md_doc(adf) == "hi @Ana\nnext\n\n---"


def test_date_and_status():
    adf = doc(para(
        {"type": "date", "attrs": {"timestamp": "1755993600000"}},
        text(" "),
        {"type": "status", "attrs": {"text": "IN PROGRESS"}},
    ))
    assert create_md_doc(adf) == "2025-08-24 [status: IN PROGRESS]"


def test_media_refs_collected():
    adf = doc(
        {"type": "mediaSingle", "content": [
            {"type": "media", "attrs": {"id": "abc-123"}}]},
        para({"type": "mediaInline", "attrs": {"url": "https://img/x.png"}}),
    )
    refs = parse_doc(adf).media_ref
    assert [(r.ref_type, r.ref) for r in refs] == [
        (MediaRefType.ID, "abc-123"),
        (MediaRefType.URL, "https://img/x.png"),
    ]


def test_media_ref_alt_and_type_are_distinct():
    adf = doc({"type": "mediaSingle", "content": [
        {"type": "media", "attrs": {
            "id": "abc-123", "type": "file", "alt": "screenshot.png",
        }},
    ]})
    ref = parse_doc(adf).media_ref[0]
    assert ref.alt == "screenshot.png"
    assert ref.media_type == "file"


def test_inline_card():
    adf = doc(para({"type": "inlineCard", "attrs": {"url": "https://jira/T-1"}}))
    result = parse_doc(adf)
    assert result.collected_text == ["https://jira/T-1"]
    assert result.links == [("https://jira/T-1", "https://jira/T-1")]


def test_panel_and_expand():
    adf = doc(
        {"type": "panel", "attrs": {"panelType": "warning"}, "content": [para(text("careful"))]},
        {"type": "expand", "attrs": {"title": "More"}, "content": [para(text("hidden"))]},
    )
    assert create_md_doc(adf) == "[warning] careful\n\n[expand: More]\nhidden"


def test_empty_doc():
    assert create_md_doc({"type": "doc", "version": 1}) == ""


def test_plain_mode_strips_marks_and_link_syntax():
    adf = doc(para(
        text("bold", {"type": "strong"}),
        text(" see "),
        text("docs", {"type": "link", "attrs": {"href": "https://x.io"}}),
        text(" and "),
        text("x=1", {"type": "code"}),
    ))
    from adf_parse import create_text_doc
    assert create_text_doc(adf) == "bold see docs and x=1"
    assert parse_doc(adf, plain=True).links == [("docs", "https://x.io")]


def test_plain_mode_drops_emoji():
    from adf_parse import create_text_doc
    adf = doc(para(
        text("Login fails "),
        {"type": "emoji", "attrs": {"shortName": ":fire:", "text": "🔥"}},
    ))
    assert create_text_doc(adf) == "Login fails "
